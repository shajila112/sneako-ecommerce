from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginActivity

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
