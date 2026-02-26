from django.db import models

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.value

class Product(models.Model):
    BRAND_CHOICES = [
        ('Nike', 'Nike'),
        ('Adidas', 'Adidas'),
        ('Puma', 'Puma'),
        ('Reebok', 'Reebok'),
        ('New Balance', 'New Balance'),
    ]

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Kids', 'Kids'),
        ('Unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0) # Total stock (can be calculated)
    image = models.ImageField(upload_to='products/', null=True, blank=True) # Main image
    image_url = models.URLField(max_length=500, null=True, blank=True) # External image URL
    is_new_arrival = models.BooleanField(default=False)
    sizes = models.ManyToManyField(Size, through='ProductSize', related_name='products', blank=True)
    
    # New Fields for Enhanced Details
    short_tagline = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    sole = models.CharField(max_length=100, null=True, blank=True)
    closure = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.name}"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - Size {self.size.value} ({self.stock})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} Image"


