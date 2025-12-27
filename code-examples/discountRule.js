function calculateDiscount(orderTotal, isLoyaltyMember) {
    if (orderTotal > 100 && isLoyaltyMember) {
        return orderTotal * 0.10;
    }
    return 0.0;
}

// Example usage
const total = 120;
const loyalty = true;
const discount = calculateDiscount(total, loyalty);
console.log(`Discount: $${discount.toFixed(2)}`);
