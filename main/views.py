import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from typing import List

from .models import UserLineItem, Product, ProductIngredient
from main.utils.pricing import calculate_default_discount, calculate_base_price, get_discount_options


# Create your views here.
def react_app_view(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({'user': {'username': user.username}})
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)  # This clears the session
    return Response({'success': True})

def get_ingredient_list(product: Product) -> str:
    ingredients = ProductIngredient.objects.filter(product=product)
    return ", ".join([str(ing) for ing in ingredients])

def build_product_data(products: List[Product], item_map: dict = None, user=None) -> List[dict]:
    """Build product list with quantities and prices."""
    product_data = []
    for product in products:
        ingredient_list = get_ingredient_list(product)
        quantity = 0
        original_quantity = 0
        base_price = float(product.wholesale)  # Default base price for guests

        if item_map:
            line_item = item_map.get(product.id)
            if line_item:
                quantity = line_item.quantity
                original_quantity = line_item.quantity
                base_price = float(calculate_base_price(user, product))

        product_data.append({
            'productId': product.id,
            'productName': product.name,
            'ingredients': ingredient_list,
            'basePrice': base_price,
            'quantity': quantity,
            'originalQuantity': original_quantity,
        })
    return product_data



@api_view(['GET'])
def user_product_list(request):
    user = request.user
    is_guest = isinstance(user, AnonymousUser) or not user.is_authenticated

    # Get all active products
    products = Product.objects.filter(isActive=True).order_by('name')
    
    product_data = []

    if is_guest:
        product_data = build_product_data(products)
        
        return Response({
            'user': None,
            'products': product_data,
            'totalBottles': 0,
            'discountPercent': 0,
        })

    # Authenticated user
    user_items = UserLineItem.objects.filter(user=user, adminOrder__isnull=True)
    item_map = {item.product.id: item for item in user_items}

    total_bottles = user_items.aggregate(total=Sum('quantity')).get('total') or 0
    discount_percent = calculate_default_discount(total_bottles)

    product_data = build_product_data(products, item_map=item_map, user=user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'is_staff': user.is_staff,
        },
        'products': product_data,
        'totalBottles': total_bottles,
        'discountPercent': discount_percent,
    })


@api_view(['GET'])
def discount_options(request):

    # Get the discount options
    options = get_discount_options()

    return Response({
        'options': options,
    })

@api_view(['GET'])
def user_past_orders(request):
    user = request.user
    
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    # Get all past orders for the user
    past_orders = UserLineItem.objects.filter(user=user, adminOrder__isnull=False).order_by('-adminOrder__orderDate')

    
    order_data = []
    for item in past_orders:
        order_data.append({
            'orderId': item.adminOrder.id,
            'orderDate': item.adminOrder.orderDate.strftime('%B %#d, %Y'),
            'productId': item.product.id,
            'productName': item.product.name,
            'quantity': item.quantity,
            'basePrice': item.basePrice,
            'percentOff': item.percentOff,
            'finalPrice': item.finalPrice,
        })

    return Response({
        'orders': order_data,
    })
