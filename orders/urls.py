from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('my-orders/', views.my_orders, name='orders'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return-order/<int:order_id>/', views.return_order, name='return_order'),
]
