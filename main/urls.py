from django.urls import path, re_path
from main.views.react_views import react_app_view
from main.views.current_order_views import user_product_list
from main.views.shared_views import discount_options
from main.views.auth_views import login_view, logout_view
from main.views.past_orders_views import user_past_orders
from main.views.admin_current_order_views import admin_current_order
from main.views.admin_past_orders_views import admin_past_orders
from main.views.frontend_app_view import FrontendAppView

urlpatterns = [
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/user-product-list/', user_product_list),
    path('api/discount-options/', discount_options),
    path('api/past-orders/', user_past_orders, name='past_orders'),
    path('api/past-order/<order_id>/', user_past_orders, name='past_order_detail'),
    path('api/admin-current-order/',admin_current_order, name='admin_current_order'),
    path('api/admin-past-orders/',admin_past_orders, name='admin_past_orders'),
    path('', react_app_view, name='home'),
    path('', FrontendAppView.as_view(), name='home'),
    re_path(r'^(?!api/).*$', FrontendAppView.as_view()),  # catch-all for React routes
]
