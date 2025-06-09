from main.models import Product, ProductIngredient
from typing import List
from main.utils.pricing import calculate_base_price

def get_ingredient_list(product: Product) -> str:
    ingredients = ProductIngredient.objects.filter(product=product)
    return ", ".join([str(ing) for ing in ingredients])

def build_product_data(products: List[Product], item_map: dict = None, user=None) -> List[dict]:
    """Build product list with quantities and prices."""
    product_data = []
    for product in products:
        ingredient_list = get_ingredient_list(product)
        quantity = 0
        original_quantity = 0
        base_price = float(product.wholesale)  # Default base price for guests

        if item_map:
            line_item = item_map.get(product.id)
            if line_item:
                quantity = line_item.quantity
                original_quantity = line_item.quantity
                base_price = float(calculate_base_price(user, product))

        product_data.append({
            'productId': product.id,
            'productName': product.name,
            'ingredients': ingredient_list,
            'basePrice': base_price,
            'quantity': quantity,
            'originalQuantity': original_quantity,
        })
    return product_data
