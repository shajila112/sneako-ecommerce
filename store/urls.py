from django.urls import path
from .views import home, shop, product_detail
app_name = 'store'

urlpatterns = [
   path('', home, name='home'), 
   path('shop/', shop, name='shop'),
   path('product/<int:pk>/', product_detail, name='product_detail'),
]