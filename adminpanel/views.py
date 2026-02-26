from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, ProductImage
from store.models import Coupon
from orders.models import Order, OrderItem
from django.contrib.auth.models import User


def admin_required(user):
    return user.is_staff


@never_cache
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    # Calculate total revenue from Paid orders
    revenue_data = Order.objects.filter(status='Paid').aggregate(Sum('total_amount'))
    total_revenue = revenue_data['total_amount__sum'] or 0.00
    
    # Items with stock <= 5
    low_stock = Product.objects.filter(stock__lte=5).count()
    
    active_users = User.objects.filter(is_active=True, is_staff=False).count()
    
    # Today's Logins
    from django.utils import timezone
    from .models import LoginActivity
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_logins = LoginActivity.objects.filter(login_time__gte=today_start).count()

    
    avg_order_value = 0.00
    if total_orders > 0:
        avg_order_value = float(total_revenue) / total_orders

    # Sales data for last 7 days
    sales_data = []
    today = timezone.now().date()
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_name = date.strftime('%a')
        day_revenue = Order.objects.filter(
            created_at__date=date, 
            status='Paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Calculate height percentage for the chart (max height 100%)
        # This is a bit arbitrary without a max revenue context, but let's assume 5000 is 100% for now
        # or calculate relative to the max in the last 7 days.
        sales_data.append({
            'day': day_name,
            'amount': float(day_revenue),
            'height': '0%' # Will calculate below
        })
    
    # Calculate relative heights for chart
    max_amount = max([item['amount'] for item in sales_data]) if sales_data else 0
    if max_amount > 0:
        for item in sales_data:
            item['height'] = f"{int((item['amount'] / max_amount) * 100)}%"
    else:
        for item in sales_data:
            item['height'] = "10%" # Minimum height if no sales

    # Top selling products
    top_products_query = OrderItem.objects.values('product_name').annotate(
        total_sales=Count('id'),
        quantity=Sum('quantity')
    ).order_by('-quantity')[:5]
    
    top_products = []
    for p in top_products_query:
        top_products.append({
            'name': p['product_name'],
            'sales': p['quantity'],
            'growth': '+0%' # Growth calculation would require historical data
        })

    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'low_stock': low_stock,
        'active_users': active_users,
        'avg_order_value': avg_order_value,
        'sales_data': sales_data,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'todays_logins': todays_logins,
    }

    return render(request, 'adminpanel/dashboard.html', context)


@never_cache
@login_required
@user_passes_test(admin_required)
def products(request):
    from products.models import Size
    from django.db.models import Q
    
    if request.method == "POST" and "add_product" in request.POST:
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        gender = request.POST.get('gender')
        sku = request.POST.get('sku')
        price = request.POST.get('price')
        original_price = request.POST.get('original_price') or None
        stock = request.POST.get('stock')
        images = request.FILES.getlist('images')
        
        # New details
        short_tagline = request.POST.get('short_tagline')
        description = request.POST.get('description')
        model_name = request.POST.get('model_name')
        color = request.POST.get('color')
        material = request.POST.get('material')
        sole = request.POST.get('sole')
        closure = request.POST.get('closure')
        selected_sizes = request.POST.getlist('sizes')

        # Calculate Total Stock
        total_stock = 0
        size_stock_data = []
        for size_id in selected_sizes:
            s_qty = request.POST.get(f'stock_{size_id}')
            qty = int(s_qty) if s_qty and s_qty.isdigit() else 0
            total_stock += qty
            size_stock_data.append({'id': size_id, 'qty': qty})

        # Handle Images
        main_image = images[0] if images else None
        main_image_url = request.POST.get('main_image_url')

        product = Product.objects.create(
            name=name,
            brand=brand,
            gender=gender,
            sku=sku,
            price=price,
            original_price=original_price,
            stock=total_stock, # Use calculated total stock
            image=main_image,
            image_url=main_image_url,
            short_tagline=short_tagline,
            description=description,
            model_name=model_name,
            color=color,
            material=material,
            sole=sole,
            closure=closure
        )

        from products.models import ProductSize
        # Handle sizes and per-size stock
        for entry in size_stock_data:
            size_obj = Size.objects.get(id=entry['id'])
            ProductSize.objects.create(
                product=product,
                size=size_obj,
                stock=entry['qty']
            )

        # Save all uploaded images to ProductImage gallery
        for img in images:
            ProductImage.objects.create(product=product, image=img)
            
        # Save image URLs to ProductImage gallery
        for i in range(1, 5):
            g_url = request.POST.get(f'gallery_url_{i}')
            if g_url:
                ProductImage.objects.create(product=product, image_url=g_url)

        return redirect('adminpanel:product_success')

    # Filtering and Searching
    products_list = Product.objects.all().order_by('-id')
    
    brand_filter = request.GET.get('brand')
    gender_filter = request.GET.get('gender')
    search_query = request.GET.get('search')

    if brand_filter and brand_filter != 'all':
        products_list = products_list.filter(brand=brand_filter)
    
    if gender_filter and gender_filter != 'all':
        products_list = products_list.filter(gender=gender_filter)
        
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model_name__icontains=search_query)
        )

    available_sizes = Size.objects.all().order_by('value')

    context = {
        'products': products_list,
        'sizes': available_sizes,
        'current_brand': brand_filter,
        'current_gender': gender_filter,
        'current_search': search_query,
    }

    return render(request, 'adminpanel/products.html', context)


@never_cache
@login_required
@user_passes_test(admin_required)
def product_success(request):
    return render(request, 'adminpanel/product_success.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    from products.models import Size
    
    if request.method == "POST":
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.gender = request.POST.get('gender')
        product.sku = request.POST.get('sku')
        product.price = request.POST.get('price')
        product.original_price = request.POST.get('original_price') or None
        product.stock = request.POST.get('stock')
        
        # New details
        product.short_tagline = request.POST.get('short_tagline')
        product.description = request.POST.get('description')
        product.model_name = request.POST.get('model_name')
        product.color = request.POST.get('color')
        product.material = request.POST.get('material')
        product.sole = request.POST.get('sole')
        product.closure = request.POST.get('closure')
        
        # Handle Images
        new_image = request.FILES.get('image')
        if new_image:
            product.image = new_image
        
        new_image_url = request.POST.get('main_image_url')
        if new_image_url:
            product.image_url = new_image_url
            
        product.save()
        
        # Handle sizes and per-size stock
        selected_sizes = request.POST.getlist('sizes')
        from products.models import ProductSize
        
        # Clear existing relations to re-add (or update)
        # Note: Using set() on ManyToMany with 'through' model requires manual handling
        # We'll calculate total stock while we're at it
        total_stock = 0
        
        # We can selectively update or just clear and recreate for simplicity
        product.product_sizes.all().delete()
        
        for size_id in selected_sizes:
            s_qty = request.POST.get(f'stock_{size_id}')
            qty = int(s_qty) if s_qty and s_qty.isdigit() else 0
            total_stock += qty
            
            size_obj = Size.objects.get(id=size_id)
            ProductSize.objects.create(
                product=product,
                size=size_obj,
                stock=qty
            )
            
        product.stock = total_stock
        product.save()
        
        # Handle multiple additional images
        additional_images = request.FILES.getlist('images')
        for img in additional_images:
            ProductImage.objects.create(product=product, image=img)
            
        # Handle gallery URLs
        for i in range(1, 5):
            g_url = request.POST.get(f'gallery_url_{i}')
            if g_url:
                ProductImage.objects.create(product=product, image_url=g_url)
            
        return redirect('adminpanel:products')
        
    available_sizes = Size.objects.all().order_by('value')
    return render(request, 'adminpanel/edit_product.html', {
        'product': product,
        'sizes': available_sizes
    })


@never_cache
@login_required
@user_passes_test(admin_required)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('adminpanel:products')


@never_cache
@login_required
@user_passes_test(admin_required)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/orders.html', {'orders': orders})


@never_cache
@login_required
@user_passes_test(admin_required)
def returns(request):
    return render(request, 'adminpanel/returns.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def inventory(request):
    return render(request, 'adminpanel/inventory.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def promo(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/promo.html', {'coupons': coupons})


@never_cache
@login_required
@user_passes_test(admin_required)
def create_coupon(request):
    if request.method == "POST":
        code = request.POST.get('code')
        discount_percentage = request.POST.get('discount_percentage')
        minimum_amount = request.POST.get('minimum_amount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        active = request.POST.get('active') == 'on'

        Coupon.objects.create(
            code=code,
            discount_percentage=discount_percentage,
            minimum_amount=minimum_amount,
            valid_from=valid_from,
            valid_to=valid_to,
            active=active
        )
    return redirect('adminpanel:promo')


@never_cache
@login_required
@user_passes_test(admin_required)
def delete_coupon(request, code):
    coupon = get_object_or_404(Coupon, code=code)
    coupon.delete()
    return redirect('adminpanel:promo')


@never_cache
@login_required
@user_passes_test(admin_required)
def users(request):
    from django.core.paginator import Paginator
    from django.db.models import Sum, Count, Q
    from .models import LoginActivity
    
    users_list = User.objects.all().annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount', filter=Q(orders__status='Paid'))
    ).order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Filtering (e.g., Active/Blocked)
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users_list = users_list.filter(is_active=True)
    elif status_filter == 'blocked':
        users_list = users_list.filter(is_active=False)

    # Identify currently logged in users
    # Users with a login activity that has no logout time
    logged_in_user_ids = LoginActivity.objects.filter(logout_time__isnull=True).values_list('user_id', flat=True).distinct()

    # Pagination
    paginator = Paginator(users_list, 10) # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'logged_in_user_ids': list(logged_in_user_ids),
    }

    return render(request, 'adminpanel/users.html', context)


@never_cache
@login_required
@user_passes_test(admin_required)
def wallet(request):
    return render(request, 'adminpanel/wallet.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def notifications(request):
    return render(request, 'adminpanel/notifications.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def reviews(request):
    return render(request, 'adminpanel/reviews.html')


@never_cache
@login_required
@user_passes_test(admin_required)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_staff:
        user.is_active = False
        user.save()
        messages.success(request, f"User {user.username} has been blocked.")
    else:
        messages.error(request, "Cannot block admin users.")
    return redirect('adminpanel:users')


@never_cache
@login_required
@user_passes_test(admin_required)
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('adminpanel:users')


@never_cache
@login_required
@user_passes_test(admin_required)
def user_detail(request, user_id):
    from django.db.models import Sum
    user = get_object_or_404(User, id=user_id)
    from .models import LoginActivity
    
    # Login History
    login_history = LoginActivity.objects.filter(user=user).order_by('-login_time')[:10]
    
    # Orders
    orders = user.orders.all().order_by('-created_at')[:5]
    
    # Stats
    total_spent = orders.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    order_count = orders.count()
    
    context = {
        'user_obj': user,
        'login_history': login_history,
        'orders': orders,
        'total_spent': total_spent,
        'order_count': order_count,
    }
    return render(request, 'adminpanel/user_detail.html', context)

    return render(request, 'adminpanel/user_detail.html', context)


@never_cache
@login_required
@user_passes_test(admin_required)
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('adminpanel:users')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('adminpanel:users')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('adminpanel:users')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            if role == 'admin':
                user.is_staff = True
                user.save()
                
            messages.success(request, f"User {username} created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")

    return redirect('adminpanel:users')


@never_cache
@login_required
@user_passes_test(admin_required)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Superuser cannot be deleted.")
    elif user.is_staff:
        messages.error(request, "Admin users cannot be deleted.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('adminpanel:users')


@never_cache
@login_required
@user_passes_test(admin_required)
def add_size(request):
    if request.method == "POST":
        from products.models import Size
        value = request.POST.get('value')
        if value:
            size, created = Size.objects.get_or_create(value=value)
            if created:
                return JsonResponse({'status': 'success', 'id': size.id, 'value': size.value})
            else:
                return JsonResponse({'status': 'exists', 'message': 'Size already exists'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@never_cache
@login_required
@user_passes_test(admin_required)
def delete_product_image(request, pk):
    image = get_object_or_404(ProductImage, pk=pk)
    product_id = image.product.id
    image.delete()
    messages.success(request, "Gallery image deleted successfully.")
    return redirect('adminpanel:edit_product', pk=product_id)
