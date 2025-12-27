using System;

class DiscountRule {
    public static double CalculateDiscount(double orderTotal, bool isLoyaltyMember) {
        if (orderTotal > 100 && isLoyaltyMember) {
            return orderTotal * 0.10;
        }
        return 0.0;
    }

    static void Main() {
        double total = 120;
        bool loyalty = true;
        double discount = CalculateDiscount(total, loyalty);
        Console.WriteLine($"Discount: ${discount:F2}");
    }
}
