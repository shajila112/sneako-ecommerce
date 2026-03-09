from django.db import models
from django.contrib.auth.models import User

class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Login Activities"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    @property
    def duration(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('login', 'User Login'),
        ('order', 'New Order'),
        ('return', 'Product Return'),
        ('stock', 'Low Stock'),
        ('payment', 'Payment Failed'),
        ('coupon', 'Coupon Expiry'),
        ('cancel_request', 'Cancellation Request'),
        ('other', 'Other'),
    ]

    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
    related_link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.message[:50]}"

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.user.username}: {self.message[:50]}"
