from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from main.models import UserOrder, UserLineItem

@api_view(['GET'])
def user_past_orders(request):
    user = request.user
    
    if not user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    # Get all past orders for the user
    past_orders = UserOrder.objects.filter(user=user, adminOrder__isnull=False).order_by('-adminOrder__orderDate')

    order_data = []
    for order in past_orders:
        line_items_qs = UserLineItem.objects.filter(userOrder=order)
        line_items = []
        for item in line_items_qs:
            line_items.append({
                'productId': item.product.id,
                'productName': item.product.name,
                'quantity': item.quantity,
                'basePrice': item.basePrice,
                'percentOff': item.percentOff,
                'finalPrice': item.finalPrice,
            })

        order_data.append({
            'orderDate': order.adminOrder.orderDate.strftime('%B %#d, %Y'),
            'shippingState': order.shippingState,
            'shippingAmount': order.shippingAmount,
            'taxAmount': order.taxAmount,
            'placedBy': order.adminOrder.placedBy.first_name,
            'lineItems': line_items,
        })

    return Response({
        'orders': order_data,
    })