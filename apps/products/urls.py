"""URL patterns for products app."""

from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("create/", views.product_create, name="product_create"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
    path("<slug:slug>/edit/", views.product_edit, name="product_edit"),
    path("<slug:slug>/delete/", views.product_delete, name="product_delete"),
    path("categories/create/", views.category_create, name="category_create"),
]
