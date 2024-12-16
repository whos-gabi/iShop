from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review, Coupon
from django.contrib import admin

ADMIN_SITE_HEADER = "iShop Admin"
ADMIN_SITE_TITLE = "iShop Admin Portal"
ADMIN_INDEX_TITLE = "Bine ai venit în panelul de administrare iShop"

admin.site.site_header = ADMIN_SITE_HEADER
admin.site.site_title = ADMIN_SITE_TITLE
admin.site.index_title = ADMIN_INDEX_TITLE

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['category', 'price']
    fieldsets = (
        ('Informații generale', {
            'fields': ('name', 'category', 'description')
        }),
        ('Detalii produs', {
            'fields': ('price', 'stock', 'image')
        }),
    )
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    list_filter = ['rating', 'created_at']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'active']
    search_fields = ['code']
    list_filter = ['active', 'valid_from', 'valid_to']
