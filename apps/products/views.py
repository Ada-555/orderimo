"""Views for products app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm, CategoryForm


def is_superuser(user):
    return user.is_superuser if user.is_authenticated else False


def product_list(request):
    """List all active products with search, filter, sort."""

    products = Product.objects.filter(status=Product.Status.ACTIVE)
    query = request.GET.get("q")
    category_slug = request.GET.get("category")
    sort = request.GET.get("sort", "-created_at")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    valid_sorts = ["price", "-price", "name", "-name", "-created_at", "created_at"]
    if sort in valid_sorts:
        products = products.order_by(sort)

    categories = Category.objects.filter(is_active=True)
    paginator = Paginator(products, 12)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": sort,
        "search_query": query or "",
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    """Product detail page."""

    product = get_object_or_404(
        Product.objects.prefetch_related("images"), slug=slug, status=Product.Status.ACTIVE
    )
    related = (
        Product.objects.filter(category=product.category, status=Product.Status.ACTIVE)
        .exclude(id=product.id)[:4]
    )
    return render(request, "products/product_detail.html", {"product": product, "related": related})


@user_passes_test(is_superuser)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created.")
            return redirect("products:product_list")
    else:
        form = ProductForm()
    return render(request, "products/product_form.html", {"form": form, "action": "Create"})


@user_passes_test(is_superuser)
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("products:product_detail", slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form, "action": "Edit"})


@user_passes_test(is_superuser)
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("products:product_list")
    return render(request, "products/product_confirm_delete.html", {"product": product})


@user_passes_test(is_superuser)
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("products:product_list")
    else:
        form = CategoryForm()
    return render(request, "products/category_form.html", {"form": form})
