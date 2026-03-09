from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginActivity, AdminNotification
from orders.models import Order
from products.models import Product

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    LoginActivity.objects.create(user=user, ip_address=ip, user_agent=user_agent)
    
    # Create Admin Notification if not staff
    if not user.is_staff:
        AdminNotification.objects.create(
            message=f"User {user.username} logged in.",
            notification_type='login',
            related_link=f"/adminpanel/users/{user.id}/"
        )

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    if user:
        try:
            # Update the latest login activity for this user that hasn't been closed
            activity = LoginActivity.objects.filter(user=user, logout_time__isnull=True).latest('login_time')
            activity.logout_time = timezone.now()
            activity.save()
        except LoginActivity.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def order_notification_handler(sender, instance, created, **kwargs):
    if created:
        AdminNotification.objects.create(
            message=f"New Order #{instance.id} received from {instance.user.username}.",
            notification_type='order',
            related_link=f"/adminpanel/orders/" # Could be more specific if detail page exists
        )
    else:
        # Check for status changes
        if instance.status == 'Return Requested':
            AdminNotification.objects.create(
                message=f"Return requested for Order #{instance.id}.",
                notification_type='return',
                related_link=f"/adminpanel/orders/{instance.id}/"
            )
        
        # Check for payment failure
        if instance.payment_status == 'Failed':
             AdminNotification.objects.create(
                message=f"Payment failed for Order #{instance.id}.",
                notification_type='payment',
                related_link=f"/adminpanel/orders/"
            )

@receiver(post_save, sender=Product)
def low_stock_notification_handler(sender, instance, **kwargs):
    if instance.stock <= 5:
        # Avoid duplicate notifications for the same low stock event if possible, 
        # but for simplicity we'll just create it. In a real-world app, we might check if one exists recently.
        AdminNotification.objects.create(
            message=f"Low stock warning: {instance.name} (Stock: {instance.stock}).",
            notification_type='stock',
            related_link=f"/adminpanel/products/"
        )
