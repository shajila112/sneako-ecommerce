import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

from products.models import Product, ProductImage

products = Product.objects.all()
for p in products:
    images = p.images.all()
    print(f"Product: {p.name} (ID: {p.id})")
    print(f"  Main image: {p.image.url if p.image else 'None'}")
    print(f"  Gallery images: {len(images)}")
    for img in images:
        print(f"    - {img.image.url if img.image else img.image_url}")
