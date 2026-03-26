"""Admin configuration for accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_verified", "is_staff", "date_joined")
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_superuser", "is_verified")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone", "avatar_url", "is_verified")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("name", "user__email", "city")
