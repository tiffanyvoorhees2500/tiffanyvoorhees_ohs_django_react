from django.urls import path
from .views import react_app_view, user_product_list, discount_options, login_view, logout_view

urlpatterns = [
    path('api/user-product-list/', user_product_list),
    path('api/discount-options/', discount_options),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('', react_app_view, name='home'),
]
