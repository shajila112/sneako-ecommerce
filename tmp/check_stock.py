import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from products.models import Product, ProductSize

try:
    product = Product.objects.get(pk=14)
    print(f"Product: {product.name}")
    print(f"Total Stock: {product.stock}")
    print("Sizes:")
    for ps in ProductSize.objects.filter(product=product):
        print(f"  Size {ps.size.value}: Stock {ps.stock}")
except Product.DoesNotExist:
    print("Product 14 does not exist.")
except Exception as e:
    print(f"Error: {e}")
