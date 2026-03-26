"""Home app — root view."""

from django.shortcuts import render
from django.db.models import Count
from apps.products.models import Product, Category


def home(request):
    categories = Category.objects.filter(is_active=True)[:8]
    products = Product.objects.filter(status=Product.Status.ACTIVE).order_by("-created_at")[:8]
    return render(request, "home/home.html", {"categories": categories, "page_obj": products})
