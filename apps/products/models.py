"""Product catalog models."""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    friendly_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-z0-9]+', '-', self.name.lower()).strip('-')
        super().save(*args, **kwargs)


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    sale_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    has_sizes = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    image = models.ImageField(upload_to="products/", blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)  # Flexible extra data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            self.slug = re.sub(r"[^\w]", "-", self.name.lower())
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Multiple images per product."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"

    def __str__(self):
        return f"{self.product.name} — {self.id}"
