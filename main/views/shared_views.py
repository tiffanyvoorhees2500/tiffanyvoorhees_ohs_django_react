from rest_framework.decorators import api_view
from rest_framework.response import Response

from main.utils.pricing import get_discount_options

@api_view(['GET'])
def discount_options(request):

    # Get the discount options
    options = get_discount_options()

    return Response({
        'options': options,
    })
