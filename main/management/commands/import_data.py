import csv
from django.core.management.base import BaseCommand
from main.models import Product, ProductIngredient, User, AdminOrder, AdminLineItem, UserOrder, UserLineItem
from django.utils.dateparse import parse_datetime
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle(self, *args, **kwargs):
        users = []
        products = []
        productIngredients = []
        adminOrders = []
        userOrders = []
        userLineItems = []
        adminLineItems = []

        ### USERS ###
        # Read and prepare user data, DO NOT use bulk create as it will not work with password hashing
        with open('main/data/users.csv', 'r') as user_file:
            reader = csv.DictReader(user_file)
            count = 0
            for row in reader:
                full_name = row['userName'].strip()
                parts = full_name.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''

                user = User(
                    username=full_name.replace(' ', '').lower(),
                    first_name=first_name,
                    last_name=last_name,
                    email=row['userEmail'],
                    is_superuser=row['isAdmin'].strip().lower() == 'yes',
                    is_staff=row['isAdmin'].strip().lower() == 'yes',
                    originalId=safe_int(row['userId'])
                )
                user.set_password('UGAbooboo25!')  # Hash the password
                user.save()  # Saves with hashed password
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} users"))

        ###  PRODUCTS ###
        # Read and prepare product data
        with open('main/data/products.csv', 'r') as product_file:
            reader = csv.DictReader(product_file)
            for row in reader:
                product = Product(
                    name=row['productName'],
                    retail=safe_decimal(row['retailPrice']),
                    wholesale=safe_decimal(row['wholesalePrice']),
                    numInBottle=safe_int(row['numInBottle']),
                    isActive=row['discontinued'] != 'True',
                    originalId=row['productId']
                )
                products.append(product)
        
        # Bulk insert products
        Product.objects.bulk_create(products)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(products)} products"))

        ### PRODUCT INGREDIENTS ###
        # Read and prepare productIngredient data
        with open('main/data/productIngredients.csv', 'r') as productIngredient_file:
            reader = csv.DictReader(productIngredient_file)
            for row in reader:
                product = Product.objects.get(originalId=row['productId'])

                productIngredient = ProductIngredient(
                    product = product,
                    ingredient=row['ingredient'],
                    amount=safe_decimal(row['numLabel']),
                    unit=row['stringLabel'],
                )
                productIngredients.append(productIngredient)
        
        # Bulk insert productIngredients
        ProductIngredient.objects.bulk_create(productIngredients)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(productIngredients)} productIngredients"))

        ### ADMIN ORDERS ###
        # Read and prepare adminOrder data
        with open('main/data/adminOrders.csv', 'r') as adminOrder_file:
            reader = csv.DictReader(adminOrder_file)
            for row in reader:
                try:
                    adminOrder = AdminOrder(
                        originalId=row['adminOrderId'],
                        orderDate=parse_date_flexible(row['orderDate']),
                        placedBy=User.objects.get(originalId=safe_int(row['placedById'])),
                        shippingState=row['adminShipToState'] == 'UT',
                        shippingAmount=safe_decimal(row['shippingAmount']),
                        taxAmount=safe_decimal(row['taxAmount'])
                    )
                    adminOrders.append(adminOrder)
                except ObjectDoesNotExist as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping admin order placed by={row['placedById']} — {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Unexpected error: {e}"
                    ))

        # Bulk insert adminOrders
        AdminOrder.objects.bulk_create(adminOrders)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(adminOrders)} adminOrders"))

        ### USER ORDERS ###
        # Read and prepare userOrder data
        with open('main/data/userOrders.csv', 'r') as userOrder_file:
            reader = csv.DictReader(userOrder_file)
            for row in reader:
                try:
                    userOrder = UserOrder(
                        user=User.objects.get(originalId=safe_int(row['userId'])),
                        adminOrder=AdminOrder.objects.get(originalId=row['adminOrderId']),
                        shippingState=row['shipToState'] == 'UT',
                        shippingAmount=safe_decimal(row['shippingAmount']),
                        taxAmount=safe_decimal(row['taxAmount'])
                    )
                    userOrders.append(userOrder)
                except ObjectDoesNotExist as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping user order with userId={row['userId']} or adminOrderId={row['adminOrderId']} — {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Unexpected error: {e}"
                    ))

        # Bulk insert userOrders
        UserOrder.objects.bulk_create(userOrders)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(userOrders)} userOrders"))

        ### USER LINE ITEMS ###
        # Read and prepare userLineItem data
        with open('main/data/userLineItems.csv', 'r') as userLineItem_file:
            reader = csv.DictReader(userLineItem_file)
            for row in reader:
                try:
                    user = User.objects.get(originalId=safe_int(row['userId']))
                    adminOrder = AdminOrder.objects.get(originalId=row['adminOrderId'])
                    userOrder = UserOrder.objects.get(user=user, adminOrder=adminOrder)

                    userLineItem = UserLineItem(
                        originalId=row['lineItemId'],
                        product=Product.objects.get(originalId=safe_int(row['productId'])),
                        user=user,
                        quantity=safe_int(row['quantity']),
                        basePrice=safe_decimal(row['lineItemBasePrice']),
                        percentOff=safe_decimal(row['percentOff']),
                        finalPrice=safe_decimal(row['lineItemSetPrice']),
                        adminOrder=adminOrder,
                        userOrder=userOrder
                    )
                    userLineItems.append(userLineItem)
                except ObjectDoesNotExist as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping user line item  — {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Unexpected error: {e}"
                    ))

        # Bulk insert userLineItems
        UserLineItem.objects.bulk_create(userLineItems)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(userLineItems)} userLineItems"))

        ### ADMIN LINE ITEMS ###
        # Read and prepare adminLineItem data
        with open('main/data/adminLineItems.csv', 'r') as adminLineItem_file:
            reader = csv.DictReader(adminLineItem_file)
            for row in reader:
                try:
                    adminLineItem = AdminLineItem(
                        originalLineItemId=row['adminLineItemId'],
                        product=Product.objects.get(originalId=safe_int(row['productId'])),
                        quantity=safe_int(row['quantity']),
                        basePrice=safe_decimal(row['adminBasePrice']),
                        percentOff=safe_decimal(row['percentOff']),
                        finalPrice=safe_decimal(row['adminSetPrice']),
                        adminOrderId=AdminOrder.objects.get(originalId=row['adminOrderId'])
                    )
                    adminLineItems.append(adminLineItem)
                except ObjectDoesNotExist as e:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping admin line item with productId={row['productId']} or adminOrderId={row['adminOrderId']} — {e}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Unexpected error: {e}"
                    ))
        
        # Bulk insert adminLineItems
        AdminLineItem.objects.bulk_create(adminLineItems)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(adminLineItems)} adminLineItems"))

def safe_decimal(val):
    try:
        # Remove common junk characters and convert
        return Decimal(val.replace('$', '').strip())
    except (InvalidOperation, AttributeError):
        return Decimal('0.00')  # or raise, or skip, depending on your preference
    
def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default  # or raise, or skip, depending on your preference
    
def parse_date_flexible(date_str):
    try:
        naive_date = datetime.strptime(date_str,'%m/%d/%Y')
        aware_date = timezone.make_aware(naive_date,timezone.get_current_timezone())
        #Try known Us-style format
        return aware_date
    except (ValueError, TypeError):
        return None