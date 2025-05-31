from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.    
class User(AbstractUser):
    #enum-like choices for user type and status
    class PricingType(models.TextChoices):
        WHOLESALE = 'WHOLESALE', 'Wholesale'
        RETAIL = 'RETAIL', 'Retail'

    class DiscountType(models.TextChoices):
        GROUP = 'GROUP', 'Group'
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'

    pricingType = models.CharField(
        max_length=10,
        choices=PricingType.choices,
        default=PricingType.WHOLESALE,
        verbose_name='OHS Pricing Type'
    )
    discountType = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.GROUP,
        verbose_name='OHS Discount Type'
    )
    originalId = models.CharField(
        max_length=3, 
        null=True, 
        blank=True,
        verbose_name='Original User ID')

    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    retail = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale = models.DecimalField(max_digits=10, decimal_places=2)
    numInBottle = models.IntegerField()
    isActive = models.BooleanField(default=True)
    originalId = models.IntegerField(
        null=True, 
        blank=True)

    def __str__(self):
        return self.name
    
class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"({self.ingredient} [{self.amount} {self.unit}])"
    
class AdminOrder(models.Model):
    originalId = models.CharField(max_length=255, null=True, blank=True)
    orderDate = models.DateTimeField()
    placedBy = models.ForeignKey(User, on_delete=models.CASCADE)
    shippingState = models.CharField(max_length=2)
    shippingAmount = models.DecimalField(max_digits=10, decimal_places=2)
    taxAmount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.orderDate.strftime('%b %d, %Y')} - Ordered by {self.placedBy}"

class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adminOrder = models.ForeignKey(AdminOrder, on_delete=models.CASCADE)
    shippingState = models.CharField(max_length=2)
    shippingAmount = models.DecimalField(max_digits=10, decimal_places=2)
    taxAmount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order by {self.user} submitted on {self.adminOrder.orderDate}"
    
class UserLineItem(models.Model):
    originalId = models.CharField(max_length=255, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    basePrice = models.DecimalField(max_digits=10, decimal_places=2)
    percentOff = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    finalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    userOrder = models.ForeignKey(UserOrder, on_delete=models.CASCADE, null=True, blank=True)
    adminOrder = models.ForeignKey(AdminOrder, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product}: ${self.basePrice} X {self.percentOff}% off = {self.quantity} @ ${self.finalPrice} = ${self.quantity * self.finalPrice}"
    
class AdminLineItem(models.Model):
    originalLineItemId = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    basePrice = models.DecimalField(max_digits=10, decimal_places=2)
    percentOff = models.DecimalField(max_digits=5, decimal_places=2)
    finalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    adminOrderId = models.ForeignKey(AdminOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product}: ${self.basePrice} X {self.percentOff}% off = {self.quantity} @ ${self.finalPrice} = ${self.quantity * self.finalPrice}"