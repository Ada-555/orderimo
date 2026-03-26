"""Plurino URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.home import home
from apps.products.api import api as products_api

handler404 = "orderimo.views.handler404"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("products/", include("apps.products.urls")),
    path("cart/", include("apps.cart.urls")),
    path("checkout/", include("apps.checkout.urls")),
    path("orders/", include("apps.orders.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("api/", products_api.urls),  # Django Ninja API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
