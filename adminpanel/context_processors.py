from .models import AdminNotification, UserNotification

def notification_context(request):
    context = {}
    if request.user.is_authenticated:
        # User Notifications
        user_unread_count = UserNotification.objects.filter(user=request.user, is_read=False).count()
        context['user_notifications_count'] = user_unread_count
        context['latest_user_notifications'] = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:5]

        # Admin Notifications
        if request.user.is_staff:
            admin_unread_count = AdminNotification.objects.filter(is_read=False).count()
            context['unread_notifications_count'] = admin_unread_count
            context['latest_admin_notifications'] = AdminNotification.objects.filter(is_read=False).order_by('-created_at')[:5]
            
    return context
