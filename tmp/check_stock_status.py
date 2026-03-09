import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\THIN 15\Desktop\SNEAKO_PROJECT\sneako_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from products.models import Product, ProductSize, Size

def check_stock_status():
    print("Checking product stock levels...")
    products = Product.objects.all()
    for product in products:
        print(f"\nProduct: {product.brand} {product.name} (ID: {product.id})")
        print(f"Total Stock: {product.stock}")
        
        product_sizes = ProductSize.objects.filter(product=product)
        if product_sizes.exists():
            print("Sizes and Stock:")
            for ps in product_sizes:
                print(f"  - Size: {ps.size.value}, Stock: {ps.stock}")
        else:
            print("No size information found.")

if __name__ == "__main__":
    check_stock_status()
