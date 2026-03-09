import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\THIN 15\Desktop\SNEAKO_PROJECT\sneako_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import UserNotification

def verify_notification_logic():
    # Get a test user
    user = User.objects.filter(is_staff=False).first()
    if not user:
        print("No non-staff user found for testing.")
        return

    print(f"Testing for user: {user.username}")

    # Create dummy notification
    notif = UserNotification.objects.create(
        user=user,
        message="Test notification for verification."
    )
    print(f"Created notification: ID {notif.id}, is_read: {notif.is_read}")

    # Test "Mark as Read" logic
    notif.is_read = True
    notif.save()
    updated_notif = UserNotification.objects.get(id=notif.id)
    print(f"After marking as read: is_read: {updated_notif.is_read}")

    # Test "Delete" logic
    notif_id = notif.id
    notif.delete()
    is_deleted = not UserNotification.objects.filter(id=notif_id).exists()
    print(f"After deletion: Exists: {not not is_deleted}")

if __name__ == "__main__":
    verify_notification_logic()
