from django.urls import path
from .views import react_app_view, user_product_list, discount_options

urlpatterns = [
    path('api/user-product-list/', user_product_list),
    path('api/discount-options/', discount_options),
    path('', react_app_view, name='home'),
]
