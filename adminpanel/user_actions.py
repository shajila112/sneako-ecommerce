from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

def admin_required(user):
    return user.is_staff

@login_required
@user_passes_test(admin_required)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_staff:
        messages.error(request, "Cannot block admin users.")
    else:
        user.is_active = False
        user.save()
        messages.success(request, f"User {user.username} has been blocked.")
    return redirect('adminpanel:users')

@login_required
@user_passes_test(admin_required)
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('adminpanel:users')
