from django.contrib.auth.models import AnonymousUser

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from main.models import UserLineItem, Product
from main.utils.pricing import calculate_default_discount
from main.utils.products import build_product_data

from django.db.models import Sum

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