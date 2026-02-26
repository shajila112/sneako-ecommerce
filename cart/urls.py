from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_view, name='payment'),
    path('pay/', views.pay_view, name='pay'),
    path('order-success/<int:order_id>/', views.order_success_view, name='order_success'),
]
