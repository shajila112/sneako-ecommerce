from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils import timezone
import decimal
from products.models import Product, Size
from .models import Cart, CartItem
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

@never_cache
@login_required(login_url='accounts:login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Session-based Coupon logic
    cart_total = float(cart.get_total_price())
    coupon_id = request.session.get('coupon_id')
    from store.models import Coupon
    coupon = None
    discount = 0
    final_total = cart_total
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            is_valid, error = coupon.is_valid(request.user, cart_total)
            if is_valid:
                discount = (coupon.discount_percentage / 100) * cart_total
                final_total = cart_total - discount
            else:
                del request.session['coupon_id']
                messages.warning(request, f"Coupon removed: {error}")
                coupon = None # Clear it for context
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
    
    # Fetch available coupons applicable to this cart and user
    now = timezone.now()
    available_coupons = Coupon.objects.filter(
        active=True, 
        valid_from__lte=now, 
        valid_to__gte=now,
        minimum_amount__lte=cart_total
    )

    # If user has previous orders, don't show first-order only coupons
    from orders.models import Order
    has_orders = Order.objects.filter(user=request.user).exclude(status='Cancelled').exists()
    if has_orders:
        available_coupons = available_coupons.exclude(is_first_order_only=True)
            
    context = {
        'cart': cart,
        'cart_total': cart_total,
        'discount': discount,
        'final_total': final_total,
        'applied_coupon': coupon,
        'available_coupons': available_coupons
    }
    return render(request, 'store/cart.html', context)

@never_cache
@login_required(login_url='accounts:login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_id = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    
    if not size_id:
        messages.error(request, "Please select a size.")
        return redirect('store:product_detail', pk=product_id)
        
    size = get_object_or_404(Size, id=size_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size
    )
    
    from products.models import ProductSize
    try:
        ps = ProductSize.objects.get(product=product, size=size)
    except ProductSize.DoesNotExist:
        messages.error(request, "This size is not available for this product.")
        return redirect('store:product_detail', pk=product_id)

    if not created:
        new_quantity = cart_item.quantity + quantity
    else:
        new_quantity = quantity

    if ps.stock < new_quantity:
        messages.error(request, f"Total quantity exceeds available stock ({ps.stock} left for size {size.value}).")
        if created:
            cart_item.delete()
        return redirect('store:product_detail', pk=product_id)

    cart_item.quantity = new_quantity
    cart_item.save()
    
    if ps.stock <= 5:
        messages.warning(request, f"{product.name} has low stock ({ps.stock} left). Hurry!")
    else:
        messages.success(request, f"{product.name} added to cart.")
    return redirect('cart:cart')

@never_cache
@login_required(login_url='accounts:login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart:cart')

@never_cache
@login_required(login_url='login')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        from products.models import ProductSize
        try:
            ps = ProductSize.objects.get(product=cart_item.product, size=cart_item.size)
            if ps.stock < quantity:
                messages.error(request, f"Quantity exceeds available stock ({ps.stock} left).")
                return redirect('cart:cart')
        except ProductSize.DoesNotExist:
            messages.error(request, "Stock information not found.")
            return redirect('cart:cart')
            
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Quantity updated for {cart_item.product.name}.")
    else:
        name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f"{name} removed from cart.")
    return redirect('cart:cart')

@never_cache
@login_required(login_url='accounts:login')
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not coupon_code:
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
                messages.info(request, "Coupon removed.")
            else:
                messages.error(request, "Please enter a coupon code.")
            return redirect('cart:cart')

        from store.models import Coupon
        try:
            # Case-insensitive match for the code
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            
            # Use get_or_create to be safe
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_total = float(cart.get_total_price())
            
            is_valid, error = coupon.is_valid(request.user, cart_total)
            if is_valid:
                request.session['coupon_id'] = coupon.id
                messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
            else:
                # If invalid, ensure it's removed from session if it was there
                if request.session.get('coupon_id') == coupon.id:
                    del request.session['coupon_id']
                messages.error(request, error)
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            
    return redirect('cart:cart')

@never_cache
@login_required(login_url='accounts:login')
def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request, "Coupon removed.")
    return redirect('cart:cart')

@never_cache
@login_required(login_url='accounts:login')
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart')
    
    from store.models import Coupon
    
    subtotal = float(cart.get_total_price())
    discount = 0
    coupon = None
    
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            is_valid, error = coupon_obj.is_valid(request.user, subtotal)
            if is_valid:
                coupon = coupon_obj
                discount = (coupon.discount_percentage / 100) * subtotal
            else:
                del request.session['coupon_id']
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
    
    # Fetch available coupons applicable to this subtotal and user
    now = timezone.now()
    available_coupons = Coupon.objects.filter(
        active=True, 
        valid_from__lte=now, # Use now instead of just date check for consistency
        valid_to__gte=now,
        minimum_amount__lte=subtotal
    )

    # If user has previous orders, don't show first-order only coupons
    from orders.models import Order
    has_orders = Order.objects.filter(user=request.user).exclude(status='Cancelled').exists()
    if has_orders:
        available_coupons = available_coupons.exclude(is_first_order_only=True)
    final_total = subtotal - discount
    
    from accounts.models import UserAddress
    saved_addresses = UserAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('cart:checkout')
        
        request.session['checkout_address_id'] = address_id
        # Forces session save to be double sure
        request.session.modified = True
        return redirect('cart:payment')

    context = {
        'cart': cart,
        'cart_total': subtotal,
        'discount': discount,
        'final_total': final_total,
        'applied_coupon': coupon,
        'available_coupons': available_coupons,
        'saved_addresses': saved_addresses,
    }
    return render(request, 'cart/checkout.html', context)

@never_cache
@login_required(login_url='accounts:login')
def payment_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect('cart:cart')
    
    address_id = request.session.get('checkout_address_id')
    if not address_id:
        messages.error(request, "Please select an address first.")
        return redirect('cart:checkout')

    from store.models import Coupon
    subtotal = float(cart.get_total_price())
    discount = 0
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            if coupon_obj.active:
                discount = (coupon_obj.discount_percentage / 100) * subtotal
        except Coupon.DoesNotExist:
            pass
            
    final_total = subtotal - discount
    
    from accounts.models import Wallet, UserAddress
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Fetch the selected address for the summary
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    context = {
        'cart': cart,
        'cart_total': subtotal,
        'discount': discount,
        'final_total': final_total,
        'user_wallet': wallet,
        'selected_address': address,
    }
    return render(request, 'cart/payment.html', context)

@never_cache
@login_required(login_url='accounts:login')
def pay_view(request):
    if request.method != 'POST':
        return redirect('cart:payment')
        
    cart = get_object_or_404(Cart, user=request.user)
    address_id = request.session.get('checkout_address_id')
    payment_method = request.POST.get('payment_method')
    
    if not address_id or not payment_method:
        messages.error(request, "Incomplete checkout details.")
        return redirect('cart:checkout')

    from store.models import Coupon
    from orders.models import Order, OrderItem, ShippingAddress
    from accounts.models import UserAddress, Wallet, WalletTransaction
    import decimal

    subtotal = float(cart.get_total_price())
    discount = 0
    coupon = None
    coupon_id = request.session.get('coupon_id')
    
    if coupon_id:
        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            is_valid, error = coupon_obj.is_valid(request.user, subtotal)
            if is_valid:
                coupon = coupon_obj
                discount = (coupon.discount_percentage / 100) * subtotal
        except Coupon.DoesNotExist:
            pass
            
    final_total = subtotal - discount
    
    # Final Stock Check
    from products.models import ProductSize
    for item in cart.items.all():
        try:
            ps = ProductSize.objects.get(product=item.product, size=item.size)
            if ps.stock < item.quantity:
                messages.error(request, f"Insufficient stock for {item.product.name} (Size: {item.size.value}). Only {ps.stock} left.")
                return redirect('cart:cart')
        except ProductSize.DoesNotExist:
            messages.error(request, f"Stock information not found for {item.product.name}.")
            return redirect('cart:cart')

    # Process Payment Status and Logic
    payment_status = 'Pending'
    order_status = 'Pending'

    if payment_method == 'WALLET':
        wallet = get_object_or_404(Wallet, user=request.user)
        if float(wallet.balance) < final_total:
            messages.error(request, "Insufficient wallet balance.")
            return redirect('cart:payment')
            
        wallet.balance -= decimal.Decimal(str(final_total))
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=final_total,
            transaction_type='DEBIT',
            description=f"Order Payment (Order Pending Creation)"
        )
        payment_status = 'Paid'
        order_status = 'Paid'

    elif payment_method == 'STRIPE':
        # Create Stripe Checkout Session
        line_items = []
        for item in cart.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.product.price * 100), # Amount in paise
                },
                'quantity': item.quantity,
            })

        try:
            # Create a PRELIMINARY Order to track the session
            # We'll finalize it in the success view
            order = Order.objects.create(
                user=request.user,
                coupon=coupon,
                subtotal=decimal.Decimal(str(subtotal)),
                discount_amount=decimal.Decimal(str(discount)),
                total_amount=decimal.Decimal(str(final_total)),
                payment_method=payment_method,
                payment_status='Pending',
                status='Pending'
            )

            # Create Shipping Address for the preliminary order
            address_obj = get_object_or_404(UserAddress, id=address_id, user=request.user)
            ShippingAddress.objects.create(
                order=order,
                full_name=address_obj.full_name,
                email=request.user.email,
                phone=address_obj.phone,
                street_address=address_obj.street_address,
                city=address_obj.city,
                state=address_obj.state,
                zip_code=address_obj.zip_code
            )

            # Create Order Items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                # Reduce Stock
                ps = ProductSize.objects.get(product=item.product, size=item.size)
                ps.reduce_stock(item.quantity)
                
                # Low Stock Notification for Admin
                if ps.stock <= 5:
                    from adminpanel.models import AdminNotification
                    AdminNotification.objects.create(
                        message=f"Low Stock Alert: {item.product.name} (Size: {item.size.value}) has only {ps.stock} items left.",
                        notification_type='stock',
                        related_link=f"/adminpanel/products/edit/{item.product.id}/"
                    )

            # Handle discounts using Stripe Coupons (negative line items are not allowed)
            discounts = []
            if discount > 0:
                stripe_coupon = stripe.Coupon.create(
                    amount_off=int(discount * 100),
                    currency='inr',
                    duration='once',
                    name=f'Discount ({coupon.code if coupon else "Coupon"})'
                )
                discounts.append({'coupon': stripe_coupon.id})

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                discounts=discounts,
                success_url=request.build_absolute_uri(reverse('cart:payment_success', kwargs={'order_id': order.id})),
                cancel_url=request.build_absolute_uri(reverse('cart:payment_cancel')),
                client_reference_id=str(order.id),
                customer_email=request.user.email,
            )
            return redirect(checkout_session.url)
        except Exception as e:
            from adminpanel.models import AdminNotification
            AdminNotification.objects.create(
                message=f"Payment Failed for Order #{order.id}: {str(e)}",
                notification_type='payment'
            )
            messages.error(request, f"Stripe error: {str(e)}")
            return redirect('cart:payment')
    
    elif payment_method == 'COD':
        payment_status = 'Pending'
        order_status = 'Pending'

    # Create Order
    order = Order.objects.create(
        user=request.user,
        coupon=coupon,
        subtotal=decimal.Decimal(str(subtotal)),
        discount_amount=decimal.Decimal(str(discount)),
        total_amount=decimal.Decimal(str(final_total)),
        payment_method=payment_method,
        payment_status=payment_status,
        status=order_status
    )
    
    # Update Wallet Transaction description if it was a wallet payment
    if payment_method == 'WALLET':
        trans = WalletTransaction.objects.filter(wallet__user=request.user).last()
        if trans:
            trans.description = f"Payment for Order #{order.id}"
            trans.save()

    # Create Shipping Address
    address_obj = get_object_or_404(UserAddress, id=address_id, user=request.user)
    ShippingAddress.objects.create(
        order=order,
        full_name=address_obj.full_name,
        email=request.user.email,
        phone=address_obj.phone,
        street_address=address_obj.street_address,
        city=address_obj.city,
        state=address_obj.state,
        zip_code=address_obj.zip_code
    )
    
    # Create Order Items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            size=item.size,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        )
        # Reduce Stock
        ps = ProductSize.objects.get(product=item.product, size=item.size)
        ps.reduce_stock(item.quantity)
        
        # Low Stock Notification for Admin
        if ps.stock <= 5:
            from adminpanel.models import AdminNotification
            AdminNotification.objects.create(
                message=f"Low Stock Alert: {item.product.name} (Size: {item.size.value}) has only {ps.stock} items left.",
                notification_type='stock',
                related_link=f"/adminpanel/products/edit/{item.product.id}/"
            )
            
    # Notify Admin of New Order (COD/Wallet)
    from adminpanel.models import AdminNotification
    AdminNotification.objects.create(
        message=f"New Order #{order.id} placed by {request.user.username} using {payment_method}.",
        notification_type='order',
        related_link=f"/adminpanel/orders/"
    )

    # Clear Cart and Session
    cart.items.all().delete()
    request.session.pop('coupon_id', None)
    request.session.pop('checkout_address_id', None)
    
    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('cart:order_success', order_id=order.id)

@never_cache
@login_required(login_url='accounts:login')
def order_success_view(request, order_id):
    from orders.models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_success.html', {'order': order})



@login_required(login_url='accounts:login')
def payment_success_view(request, order_id):
    from orders.models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Finalize Order
    order.payment_status = 'Paid'
    order.status = 'Paid'
    order.save()
    
    # Notify Admin of New Order (Stripe)
    from adminpanel.models import AdminNotification
    AdminNotification.objects.create(
        message=f"New Stripe Order #{order.id} placed by {request.user.username}.",
        notification_type='order',
        related_link=f"/adminpanel/orders/"
    )
    
    # Clear Cart
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    
    # Clear Session
    request.session.pop('coupon_id', None)
    request.session.pop('checkout_address_id', None)
    
    messages.success(request, "Payment successful! Your order has been placed.")
    return redirect('cart:order_success', order_id=order.id)

@login_required(login_url='accounts:login')
def payment_cancel_view(request):
    messages.warning(request, "Payment was cancelled. You can try again.")
    # Notify admin about payment cancellation
    from adminpanel.models import AdminNotification
    AdminNotification.objects.create(
        message=f"User {request.user.username} cancelled their Stripe payment.",
        notification_type='payment'
    )
    return redirect('cart:payment')

stripe.api_key = settings.STRIPE_SECRET_KEY

# Removed redundant create_checkout_session since it's now integrated into pay_view
