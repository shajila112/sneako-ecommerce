from django.urls import path
from .views import (
    admin_dashboard, products, admin_orders, returns, 
    inventory, promo, create_coupon, delete_coupon, delete_product, edit_product,
    add_product, product_success, users, wallet, notifications, reviews,
    block_user, unblock_user, user_detail, add_user, delete_user, add_size,
    delete_product_image, edit_coupon, toggle_coupon, admin_order_detail,
    notifications_mark_all_read, mark_notification_read,
    approve_return, reject_return,
    approve_cancellation, reject_cancellation
)

app_name = "adminpanel"

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('products/', products, name='products'),
    path('products/add/', add_product, name='add_product'),
    path('products/success/', product_success, name='product_success'),
    path('products/delete/<int:pk>/', delete_product, name='delete_product'),
    path('products/edit/<int:pk>/', edit_product, name='edit_product'),
    path('orders/', admin_orders, name='orders'),
    path('returns/', returns, name='returns'),
    path('inventory/', inventory, name='inventory'),
    path('promo/', promo, name='promo'),
    path('promo/create/', create_coupon, name='create_coupon'),
    path('promo/edit/<str:code>/', edit_coupon, name='edit_coupon'),
    path('promo/toggle/<str:code>/', toggle_coupon, name='toggle_coupon'),
    path('promo/delete/<str:code>/', delete_coupon, name='delete_coupon'),
    path('users/', users, name='users'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/block/<int:user_id>/', block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', unblock_user, name='unblock_user'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('wallet/', wallet, name='wallet'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-all-read/', notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('reviews/', reviews, name='reviews'),
    path('sizes/add/', add_size, name='add_size'),
    path('products/image/delete/<int:pk>/', delete_product_image, name='delete_product_image'),
    path('orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('orders/approve-return/<int:order_id>/', approve_return, name='approve_return'),
    path('orders/reject-return/<int:order_id>/', reject_return, name='reject_return'),
    path('orders/approve-cancellation/<int:order_id>/', approve_cancellation, name='approve_cancellation'),
    path('orders/reject-cancellation/<int:order_id>/', reject_cancellation, name='reject_cancellation'),
]
