import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import AdminNotification, LoginActivity
from orders.models import Order
from products.models import Product, Size, ProductSize
from django.utils import timezone

def verify():
    print("--- Starting Verification ---")
    
    # 1. Test User Login Notification (Simulated)
    print("Testing Login Notification...")
    user = User.objects.filter(is_staff=False).first()
    if not user:
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    
    from django.contrib.auth.signals import user_logged_in
    # We need a mock request for the signal
    class MockRequest:
        META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'TestAgent'}
    
    user_logged_in.send(sender=User, request=MockRequest(), user=user)
    
    last_notif = AdminNotification.objects.filter(notification_type='login').first()
    if last_notif and user.username in last_notif.message:
        print(f"✅ Login Notification Success: {last_notif.message}")
    else:
        print("❌ Login Notification Failed")

    # 2. Test New Order Notification
    print("Testing New Order Notification...")
    order = Order.objects.create(
        user=user,
        total_amount=100.00,
        payment_method='COD',
        status='Pending'
    )
    last_notif = AdminNotification.objects.filter(notification_type='order').first()
    if last_notif and f"#{order.id}" in last_notif.message:
        print(f"✅ New Order Notification Success: {last_notif.message}")
    else:
        print("❌ New Order Notification Failed")

    # 3. Test Return Notification
    print("Testing Return Notification...")
    order.status = 'Return Requested'
    order.save()
    last_notif = AdminNotification.objects.filter(notification_type='return').first()
    if last_notif and f"#{order.id}" in last_notif.message:
        print(f"✅ Return Notification Success: {last_notif.message}")
    else:
        print("❌ Return Notification Failed")

    # 4. Test Low Stock Notification
    print("Testing Low Stock Notification...")
    product = Product.objects.first()
    if not product:
        product = Product.objects.create(name="Test Shoe", brand="Nike", price=50.00, stock=10)
    
    product.stock = 3
    product.save()
    last_notif = AdminNotification.objects.filter(notification_type='stock').first()
    if last_notif and product.name in last_notif.message:
        print(f"✅ Low Stock Notification Success: {last_notif.message}")
    else:
        print("❌ Low Stock Notification Failed")

    # 5. Clean up test data
    # order.delete()
    # if user.username == 'testuser': user.delete()
    
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify()
