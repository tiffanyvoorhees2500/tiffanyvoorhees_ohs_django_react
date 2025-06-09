from django.contrib.auth.models import AnonymousUser

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from main.models import UserLineItem
from main.utils.pricing import calculate_default_discount

@api_view(['GET'])
def admin_current_order(request):
    user = request.user
    is_guest = isinstance(user, AnonymousUser) or not user.is_authenticated
    
    if not user.is_staff or is_guest:
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

    print("Admin current order view accessed by user:", user.username)

    # Authenticated & Authorized user
    unordered_items = UserLineItem.objects.filter(adminOrder__isnull=True)

    total_bottles = unordered_items.aggregate(total=Sum('quantity')).get('total') or 0
    discount_percent = calculate_default_discount(total_bottles)

    return Response({
        'user': {
            'id': unordered_items.user.id,
            'username': unordered_items.user.username,
            'first_name': unordered_items.user.first_name,
            'is_staff': unordered_items.user.is_staff,
        },
        'unordered_items': unordered_items,
        'totalBottles': total_bottles,
        'discountPercent': discount_percent,
    })