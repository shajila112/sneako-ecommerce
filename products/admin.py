from django.contrib import admin
from .models import Product, Size, ProductSize, ProductImage


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model_name', 'sku', 'price', 'stock', 'gender')
    list_filter = ('brand', 'gender')
    search_fields = ('name', 'sku')
    inlines = [ProductSizeInline, ProductImageInline]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('value',)
    ordering = ('value',)
