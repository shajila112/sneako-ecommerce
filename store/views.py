from products.models import Product, Size
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.cache import never_cache

@never_cache
def home(request):
    from store.models import Coupon
    from django.utils import timezone
    now = timezone.now()
    available_coupons = Coupon.objects.filter(active=True, valid_from__lte=now, valid_to__gte=now)
    best_discount_percentage = available_coupons.order_by('-discount_percentage').first().discount_percentage if available_coupons.exists() else 0
    
    products = Product.objects.all().order_by('-id')
    return render(request, 'store/index.html', {
        'products': products, 
        'available_coupons': available_coupons,
        'best_discount_percentage': best_discount_percentage
    })

@never_cache
def shop(request):
    from store.models import Coupon
    from django.utils import timezone
    now = timezone.now()
    available_coupons = Coupon.objects.filter(active=True, valid_from__lte=now, valid_to__gte=now)
    best_discount_percentage = available_coupons.order_by('-discount_percentage').first().discount_percentage if available_coupons.exists() else 0
    
    products = Product.objects.all().order_by('-id')
    
    # Get filters from request
    q_search = request.GET.get('q')
    q_gender = request.GET.getlist('gender')
    q_brand = request.GET.getlist('brand')
    q_size = request.GET.get('size')
    q_min_price = request.GET.get('min_price')
    q_max_price = request.GET.get('max_price')

    # Apply filters
    if q_search:
        products = products.filter(
            Q(name__icontains=q_search) | 
            Q(brand__icontains=q_search) | 
            Q(description__icontains=q_search) |
            Q(model_name__icontains=q_search)
        )
    if q_gender:
        products = products.filter(gender__in=q_gender)
    if q_brand:
        products = products.filter(brand__in=q_brand)
    if q_size:
        products = products.filter(sizes__value=q_size)
    if q_min_price:
        products = products.filter(price__gte=q_min_price)
    if q_max_price:
        products = products.filter(price__lte=q_max_price)

    # Context data for the sidebar
    brands = [choice[0] for choice in Product.BRAND_CHOICES]
    genders = [choice[0] for choice in Product.GENDER_CHOICES]
    sizes = Size.objects.all().order_by('value')

    context = {
        'products': products,
        'brands': brands,
        'genders': genders,
        'sizes': sizes,
        'selected_genders': q_gender,
        'selected_brands': q_brand,
        'selected_size': q_size,
        'min_price': q_min_price,
        'max_price': q_max_price,
        'available_coupons': available_coupons,
        'best_discount_percentage': best_discount_percentage,
    }
    return render(request, 'store/shop.html', context)


@never_cache
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    from store.models import Coupon
    from django.utils import timezone
    now = timezone.now()
    available_coupons = Coupon.objects.filter(active=True, valid_from__lte=now, valid_to__gte=now)

    discount_amount = None
    discount_percentage = None
    if product.original_price and product.original_price > product.price:
        discount_amount = product.original_price - product.price
        discount_percentage = round((discount_amount / product.original_price) * 100)
    
    # Calculate potential coupon savings
    best_coupon = None
    best_discounted_price = float(product.price)
    if available_coupons.exists():
        # Find the coupon with the highest percentage that might apply
        best_coupon = available_coupons.order_by('-discount_percentage').first()
        if best_coupon:
            discount = (best_coupon.discount_percentage / 100) * float(product.price)
            best_discounted_price = float(product.price) - discount

    # Related products
    related_products = Product.objects.filter(
        brand=product.brand
    ).exclude(pk=product.pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'discount_amount': discount_amount,
        'discount_percentage': discount_percentage,
        'available_coupons': available_coupons,
        'best_coupon': best_coupon,
        'best_discounted_price': best_discounted_price,
    }

    return render(request, 'store/product_detail.html', context)



