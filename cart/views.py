from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils import timezone
import decimal
from products.models import Product, Size
from .models import Cart, CartItem

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
    
    # Fetch available coupons
    now = timezone.now()
    available_coupons = Coupon.objects.filter(
        active=True, 
        valid_from__lte=now, 
        valid_to__gte=now
    )
            
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
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    
    cart_item.save()
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
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
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
    
    available_coupons = Coupon.objects.filter(active=True, valid_to__gte=timezone.now())
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
        # Mocking Stripe success for now - typically handles via webhook/checkout session
        payment_status = 'Paid'
        order_status = 'Paid'
    
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
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
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
