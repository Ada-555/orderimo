"""Order models — persisted, not session-based."""

import uuid
from django.db import models
from django.conf import settings
from django.db.models import Sum
from apps.products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order_number = models.CharField(max_length=32, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    # Customer details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    # Delivery address
    address_line1 = models.CharField(max_length=80)
    address_line2 = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=40)
    county = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2)  # ISO code
    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Stripe
    stripe_pid = models.CharField(max_length=254, blank=True)
    # Status
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    # Meta
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:16].upper()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Snapshot at time of order
    product_sku = models.CharField(max_length=50)
    size = models.CharField(max_length=10, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
