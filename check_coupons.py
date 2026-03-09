import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from store.models import Coupon

def check_coupons():
    coupons = Coupon.objects.all()
    if not coupons.exists():
        print("No coupons found in the database.")
        # Create a sample coupon if none exists, as requested by 'add real value'
        new_coupon = Coupon.objects.create(
            code="HEYY",
            discount_percentage=50,
            minimum_amount=500.0,
            active=True
        )
        print(f"Created real coupon: {new_coupon.code} with min order ₹{new_coupon.minimum_amount}")
    else:
        for coupon in coupons:
            print(f"Coupon: {coupon.code}, Discount: {coupon.discount_percentage}%, Min Order: ₹{coupon.minimum_amount}")
            if coupon.minimum_amount == 0:
                print(f"Updating {coupon.code} to have a real minimum amount (e.g., 500)")
                coupon.minimum_amount = 500.0
                coupon.save()

if __name__ == "__main__":
    check_coupons()
