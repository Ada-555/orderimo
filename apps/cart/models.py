"""Database-persisted cart — survives restarts unlike session-based."""

from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()


class Cart(models.Model):
    """One cart per user (or anonymous session)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="carts"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart {self.id} ({self.user or self.session_key})"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal
        return total

    @property
    def delivery_cost(self):
        from django.conf import settings
        threshold = float(settings.FREE_DELIVERY_THRESHOLD)
        if self.subtotal >= threshold:
            return 0
        return round(self.subtotal * float(settings.STANDARD_DELIVERY_PERCENTAGE) / 100, 2)

    @property
    def grand_total(self):
        return self.subtotal + self.delivery_cost


class CartItem(models.Model):
    """Line item in a cart."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, blank=True)  # XS, S, M, L, XL, XXL
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ("cart", "product", "size")

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.size or 'N/A'})"

    @property
    def subtotal(self):
        price = self.product.current_price
        return float(price) * self.quantity
