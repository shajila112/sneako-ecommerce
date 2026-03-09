from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib import messages
from products.models import Product
from .models import Wishlist, WishlistItem

@never_cache
@login_required(login_url='accounts:login')
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'store/wishlist_fixed.html', {'wishlist': wishlist})

@never_cache
@login_required(login_url='accounts:login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} added to wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
        
    return redirect('wishlist')

@never_cache
@login_required(login_url='login')
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    wishlist_item.delete()
    messages.info(request, "Item removed from wishlist.")
    return redirect('wishlist')
