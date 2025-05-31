from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, ProductIngredient, AdminOrder, AdminLineItem, UserOrder, UserLineItem, User as CustomUser

# Customize the UserAdmin to include the new fields
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # List of fields to display in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'pricingType', 'discountType', 'is_active', 'is_staff')
    
    # Fields to search by in the admin interface
    search_fields = ('username', 'email')

    # Filters to use in the list view (e.g., you can filter by pricingType or discountType)
    list_filter = ('is_staff', 'is_active', 'pricingType', 'discountType')

    # The fieldsets control how the form appears when adding/editing a user in the admin interface
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('User Options', {'fields': ('pricingType', 'discountType', 'originalId')}),  # Add your custom fields here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # You can also define which fields are editable directly in the form view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'pricingType', 'discountType', 'originalId', 'is_active', 'is_staff')  # Add your custom fields here,
        }),
    )

# Re-register the customer User model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)  # Register the custom User model with the customized admin

# Custom admin for Product
class ProductAdmin(admin.ModelAdmin):
    # Sort products by name by default
    ordering = ('name',)  # Default ordering by name

    # List of fields to display in the list view
    list_display = ('name', 'wholesale', 'retail', 'numInBottle', 'isActive')
    
    # Fields to search by in the admin interface
    search_fields = ('name',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Custom admin for ProductIngredients
class ProductIngredientAdmin(admin.ModelAdmin):

    # Sort products by name by default
    ordering = ('product__name', 'ingredient')  # Default ordering by name

    # List of fields to display in the list view
    list_display = ('product__name', 'ingredient', 'amount', 'unit')
    
    # Fields to search by in the admin interface
    search_fields = ('ingredient',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    
#Inline lineItems for AdminOrder
class AdminLineItemInline(admin.TabularInline):
    model = AdminLineItem
    extra = 1  # Number of empty forms to display

# Custom admin for AdminOrder
class AdminOrderAdmin(admin.ModelAdmin):
    ordering = ('-orderDate',)  # Default ordering by order date (newest first)

    inlines = [AdminLineItemInline]  # Include the inline for line items

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# class AdminLineItemAdmin(admin.ModelAdmin):
#     def has_change_permission(self, request, obj=None):
#         return request.user.is_superuser

#     def has_add_permission(self, request):
#         return request.user.is_superuser

#     def has_delete_permission(self, request, obj=None):
#         return request.user.is_superuser

# Registering with restrictions
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductIngredient, ProductIngredientAdmin)
admin.site.register(AdminOrder, AdminOrderAdmin)

# Registering others with default permissions
admin.site.register(UserOrder)
admin.site.register(UserLineItem)
