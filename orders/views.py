from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.contrib import messages
from accounts.models import Wallet, WalletTransaction
from adminpanel.models import AdminNotification
import decimal

@login_required(login_url='accounts:login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).exclude(status='Cancelled').order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required(login_url='accounts:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required(login_url='accounts:login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status not in ['Pending', 'Processing', 'Paid']:
        messages.error(request, "This order cannot be cancelled at this stage.")
        return redirect('orders:order_detail', order_id=order.id)
    
    # Update status to Cancellation Requested
    order.status = 'Cancellation Requested'
    order.save()
    
    # Notify Admin
    AdminNotification.objects.create(
        message=f"Order cancellation requested for #SNK-{order.id} by {request.user.username}.",
        notification_type='cancel_request',
        related_link=f"/adminpanel/orders/{order.id}/"
    )
    
    messages.success(request, "Cancellation request submitted. Awaiting admin approval.")
    return redirect('orders:order_detail', order_id=order.id)

@login_required(login_url='accounts:login')
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'Delivered':
        messages.error(request, "Only delivered orders can be returned.")
        return redirect('orders:order_detail', order_id=order.id)
    
    # Update status to Return Requested
    order.status = 'Return Requested'
    order.save()
    
    # Notify Admin of Return Request
    from adminpanel.models import AdminNotification
    AdminNotification.objects.create(
        message=f"Return requested for Order #SNK-{order.id} by {request.user.username}.",
        notification_type='return',
        related_link=f"/adminpanel/orders/"
    )
    
    messages.success(request, f"Return requested for Order #SNK-{order.id}. Awaiting admin approval.")
    return redirect('orders:order_detail', order_id=order.id)
