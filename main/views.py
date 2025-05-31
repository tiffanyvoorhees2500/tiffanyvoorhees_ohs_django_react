from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserLineItem, Product, ProductIngredient
from django.db.models import Sum

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from main.utils.pricing import calculate_default_discount, calculate_base_price, get_discount_options

# Create your views here.
def react_app_view(request):
    return render(request, 'index.html')


@api_view(['GET'])
def user_product_list(request):
    user = request.user
    is_guest = isinstance(user, AnonymousUser) or not user.is_authenticated

    # Get all active products
    products = Product.objects.filter(isActive=True).order_by('name')
    
    product_data = []
    
    if is_guest:
        for product in products:
            ingredients = ProductIngredient.objects.filter(product=product)
            ingredient_list = ", ".join([str(ing) for ing in ingredients])

            product_data.append({
                'productId': product.id,
                'productName': product.name,
                'ingredients': ingredient_list,
                'basePrice': float(product.wholesale),  # Use default base price
                'quantity': 0,
                'originalQuantity': 0,
            })

        return Response({
            'user': {
                'id': user.id,
                'first_name': 'Guest',
                'is_staff': False,
                'can_order': False,  # only approved users can order
            },
            'products': product_data,
            'totalBottles': 0,
            'discountPercent': 0,
        })

    # For authenticated users:
    user_items = UserLineItem.objects.filter(user=user, adminOrder__isnull=True)
    item_map = {item.product.id: item for item in user_items}

    calc_total_bottles = user_items.aggregate(total=Sum('quantity'))
    total_bottles = calc_total_bottles.get('total') or 0
    discount_percent = calculate_default_discount(total_bottles)

    for product in products:
        line_item = item_map.get(product.id)
        ingredients = ProductIngredient.objects.filter(product=product)
        ingredient_list = ", ".join([str(ing) for ing in ingredients])
        base_price = calculate_base_price(user, product)

        product_data.append({
            'productId': product.id,
            'productName': product.name,
            'ingredients': ingredient_list,
            'basePrice': float(base_price),
            'quantity': line_item.quantity if line_item else 0,
            'originalQuantity': line_item.quantity if line_item else 0,
        })

    return Response({
        'user': {
            'id': user.id,
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

@csrf_exempt
def google_auth_view(request):
    import json
    from django.contrib.auth.models import User
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    data = json.loads(request.body)
    token = data.get('token')

    print('Received token from frontend:', token)

    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), '787020493248-fht306lh2aooilurtklvkqshqne559up.apps.googleusercontent.com')
        print('Token verified. ID info:', idinfo)
        
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')

        try:
            user = User.objects.get(email=email)
            login(request, user)
            return JsonResponse({
                'user': {
                    'userId': user.id,
                    'first_name': user.first_name,
                    'is_staff': user.is_staff,
                    'can_order': True,
                }
            })
        except User.DoesNotExist:
            user = User.objects.create_user(username=email, email=email, first_name=first_name)
            user.is_staff = False
            user.save()
            login(request, user)
            return JsonResponse({
                'user': {
                    'userId': user.id,
                    'first_name': user.first_name,
                    'is_staff': user.is_staff,
                    'can_order': False,
                }
            })


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
