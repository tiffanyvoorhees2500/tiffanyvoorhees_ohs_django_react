from django.contrib.auth.models import AnonymousUser

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from main.models import UserLineItem, AdminOrder, AdminLineItem, UserOrder

@api_view(['GET'])
def admin_past_orders(request):
    user = request.user
    is_guest = isinstance(user, AnonymousUser) or not user.is_authenticated

    if not user.is_staff or is_guest:
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

    past_orders = AdminOrder.objects.all().order_by('orderDate')

    order_data = []

    for order in past_orders:
        admin_line_items = AdminLineItem.objects.filter(adminOrderId=order)
        line_items = []
        
        user_orders = UserOrder.objects.filter(
            adminOrder=order 
        )

        user_orders_data = []
        for uo in user_orders:
            user_orders_data.append({
                'id': uo.id,
                'shippingAmount': uo.shippingAmount,
                'taxAmount': uo.taxAmount,
                'lineItems': [
                    {
                        'product': uli.product.name,
                        'quantity': uli.quantity,
                        'finalPrice': uli.finalPrice,
                    }
                    for uli in UserLineItem.objects.filter(userOrder=uo)
                ],
                'user': {
                    'id': uo.user.id,
                    'first_name': uo.user.first_name,
                    'email': uo.user.email,
                },
            })

        for admin_item in admin_line_items:
            # Get all user line items for the same product in this admin order
            user_line_items = UserLineItem.objects.filter(
                adminOrder=order, product=admin_item.product
            )

            user_items_data = []
            for user_item in user_line_items:
                user_order = user_item.userOrder
                user_items_data.append({
                    'user': user_order.user.first_name,
                    'quantity': user_item.quantity,
                    'finalPrice': user_item.finalPrice,
                    'userOrderId': user_order.id,
                    'userOrderLink': f'/past-order/{user_order.id}'  # Adjust path as needed
                })

            line_items.append({
                'productId': admin_item.product.id,
                'productName': admin_item.product.name,
                'quantity': admin_item.quantity,
                'basePrice': admin_item.basePrice,
                'percentOff': admin_item.percentOff,
                'finalPrice': admin_item.finalPrice,
                'userLineItems': user_items_data
            })

        order_data.append({
            'orderDate': order.orderDate.strftime('%B %#d, %Y'),
            'shippingState': order.shippingState,
            'shippingAmount': order.shippingAmount,
            'taxAmount': order.taxAmount,
            'placedBy': order.placedBy.first_name,
            'lineItems': line_items,
            'userOrders': user_orders_data
        })

    return Response({'orders': order_data})