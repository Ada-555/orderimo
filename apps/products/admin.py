"""Admin for products app."""

from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "friendly_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "sale_price", "status", "stock")
    list_filter = ("status", "category", "is_available")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("status", "stock")
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {"fields": ("name", "slug", "sku", "category")}),
        ("Pricing", {"fields": ("price", "sale_price")}),
        ("Stock & Status", {"fields": ("stock", "is_available", "status", "has_sizes")}),
        ("Description", {"fields": ("description", "image", "image_url")}),
        ("Meta", {"fields": ("rating", "metadata"), "classes": ("collapse",)}),
    )
