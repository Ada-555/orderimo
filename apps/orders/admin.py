"""Admin for orders app."""

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "product_sku", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "email", "status", "grand_total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "full_name", "email")
    readonly_fields = ("order_number", "stripe_pid", "created_at", "updated_at")
    inlines = [OrderItemInline]

    fieldsets = (
        ("Order Info", {"fields": ("order_number", "user", "status", "note", "stripe_pid")}),
        ("Customer", {"fields": ("full_name", "email", "phone")}),
        ("Delivery", {"fields": ("address_line1", "address_line2", "city", "county", "postcode", "country")}),
        ("Totals", {"fields": ("subtotal", "delivery_cost", "grand_total")}),
    )
