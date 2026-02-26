from django.urls import path
from .views import (
    admin_dashboard, products, admin_orders, returns, 
    inventory, promo, create_coupon, delete_coupon, delete_product, edit_product,
    product_success, users, wallet, notifications, reviews,
    block_user, unblock_user, user_detail, add_user, delete_user, add_size,
    delete_product_image
)

app_name = "adminpanel"

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('products/', products, name='products'),
    path('products/success/', product_success, name='product_success'),
    path('products/delete/<int:pk>/', delete_product, name='delete_product'),
    path('products/edit/<int:pk>/', edit_product, name='edit_product'),
    path('orders/', admin_orders, name='orders'),
    path('returns/', returns, name='returns'),
    path('inventory/', inventory, name='inventory'),
    path('promo/', promo, name='promo'),
    path('promo/create/', create_coupon, name='create_coupon'),
    path('promo/delete/<str:code>/', delete_coupon, name='delete_coupon'),
    path('users/', users, name='users'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/block/<int:user_id>/', block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', unblock_user, name='unblock_user'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('wallet/', wallet, name='wallet'),
    path('notifications/', notifications, name='notifications'),
    path('reviews/', reviews, name='reviews'),
    path('sizes/add/', add_size, name='add_size'),
    path('products/image/delete/<int:pk>/', delete_product_image, name='delete_product_image'),
]