import os
import django
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from store.models import Coupon

def test_coupon_creation():
    code = "TESTPROMO2026"
    discount = 15
    min_amount = 500.0
    valid_from = timezone.now()
    valid_to = valid_from + timedelta(days=30)
    
    # Clean up if exists
    Coupon.objects.filter(code=code).delete()
    
    try:
        coupon = Coupon.objects.create(
            code=code,
            discount_percentage=discount,
            minimum_amount=min_amount,
            valid_from=valid_from,
            valid_to=valid_to,
            active=True,
            is_first_order_only=False
        )
        print(f"Successfully created coupon: {coupon.code}")
        
        # Verify
        fetched = Coupon.objects.get(code=code)
        assert fetched.discount_percentage == discount
        assert fetched.minimum_amount == min_amount
        print("Verification successful!")
        
        # Clean up
        coupon.delete()
        print("Test coupon deleted.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_coupon_creation()
