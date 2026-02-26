from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'minimum_amount', 'is_first_order_only', 'valid_from', 'valid_to', 'active')
    list_filter = ('active', 'is_first_order_only', 'valid_from', 'valid_to')
    search_fields = ('code',)
