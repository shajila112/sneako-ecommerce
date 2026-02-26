from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from .models import Product


def admin_required(user):
    return user.is_staff


@never_cache
@login_required
@user_passes_test(admin_required)
def products(request):

    if request.method == "POST":
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        gender = request.POST.get('gender')
        sku = request.POST.get('sku')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        Product.objects.create(
            name=name,
            brand=brand,
            gender=gender,
            sku=sku,
            price=price,
            stock=stock,
            image=image
        )

    products = Product.objects.all()
    return render(request, 'adminpanel/products.html', {'products': products})


@never_cache
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})
