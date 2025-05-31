def calculate_default_discount(total_bottles: int) -> float:
    """
    Calculate the default discount based on the number of bottles.
    
    Args:
        total_bottles (int): The total number of bottles in the order.
        
    Returns:
        float: The discount percentage.
    """
    if total_bottles >= 70:
        return 0.18
    elif total_bottles >= 35:
        return 0.15
    elif total_bottles >= 15:
        return 0.10
    else:
        return 0.00
    
def get_discount_options(selected_discount=None):
    options = [
        (0.00, "0-14 Bottles [0% Off]"),
        (0.10, "15-34 Bottles [10% Off]"),
        (0.15, "35-69 Bottles [15% Off]"),
        (0.18, "70+ Bottles [18% Off]"),
        (0.20, "Phone Call [20% Off]"),
    ]

    return options

def calculate_base_price(user, product):
    """
    Calculate the base price of a product for a user.
    """
    if user.pricingType == 'WHOLESALE':
        return product.wholesale
    elif user.pricingType == 'RETAIL':
        return product.retail
    else:
        return 0

