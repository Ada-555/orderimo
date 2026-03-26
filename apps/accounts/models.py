"""Custom User model for Plurino."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user with additional fields."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    avatar_url = models.URLField(max_length=500, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email


class Address(models.Model):
    """User delivery/billing addresses."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )
    name = models.CharField(max_length=100)
    line1 = models.CharField(max_length=80)
    line2 = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=40)
    county = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2)  # ISO country code
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.name} — {self.city}"
