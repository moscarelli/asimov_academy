def calculate_discount(order_total, is_loyalty_member):
    """Returns the discount amount for the order."""
    if order_total > 100 and is_loyalty_member:
        return order_total * 0.10
    return 0.0

# Example usage
if __name__ == "__main__":
    total = 120
    loyalty = True
    discount = calculate_discount(total, loyalty)
    print(f"Discount: ${discount:.2f}")
