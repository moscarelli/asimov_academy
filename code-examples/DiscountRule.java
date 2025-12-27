public class DiscountRule {
    public static double calculateDiscount(double orderTotal, boolean isLoyaltyMember) {
        if (orderTotal > 100 && isLoyaltyMember) {
            return orderTotal * 0.10;
        }
        return 0.0;
    }

    public static void main(String[] args) {
        double total = 120;
        boolean loyalty = true;
        double discount = calculateDiscount(total, loyalty);
        System.out.printf("Discount: $%.2f\n", discount);
    }
}
