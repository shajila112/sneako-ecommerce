from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount percentage (e.g. 10 for 10%)")
    minimum_amount = models.FloatField(default=0.0, help_text="Minimum order amount to apply this coupon")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    is_first_order_only = models.BooleanField(default=False, help_text="If checked, this coupon can only be used on the first order")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self, user=None, cart_total=0):
        now = timezone.now()
        
        if not self.active:
            return False, "Coupon is inactive."
            
        if not (self.valid_from <= now <= self.valid_to):
            return False, "Coupon is expired or not yet valid."
            
        if cart_total < self.minimum_amount:
            return False, f"Minimum order amount of ₹{self.minimum_amount} required."
            
        if self.is_first_order_only and user and user.is_authenticated:
            from orders.models import Order
            if Order.objects.filter(user=user).exclude(status='Cancelled').exists():
                return False, "This coupon is only for first-time customers."
                
        return True, ""
