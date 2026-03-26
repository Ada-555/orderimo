"""REST API for products app."""

from django.http import Http404
from ninja import NinjaAPI
from .models import Product, Category

api = NinjaAPI(urls_namespace="products:api")


@api.get("/products")
def list_products(request, category: str = None, search: str = None):
    qs = Product.objects.filter(status=Product.Status.ACTIVE)
    if category:
        qs = qs.filter(category__slug=category)
    if search:
        qs = qs.filter(name__icontains=search)
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "price": str(p.price),
            "sale_price": str(p.sale_price) if p.sale_price else None,
            "image": p.image.url if p.image else p.image_url,
            "sku": p.sku,
        }
        for p in qs
    ]


@api.get("/products/{slug}")
def get_product(request, slug: str):
    p = Product.objects.filter(slug=slug, status=Product.Status.ACTIVE).first()
    if not p:
        raise Http404("Product not found")
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "price": str(p.price),
        "sale_price": str(p.sale_price) if p.sale_price else None,
        "stock": p.stock,
        "has_sizes": p.has_sizes,
        "image": p.image.url if p.image else p.image_url,
        "sku": p.sku,
        "category": p.category.name if p.category else None,
    }


@api.get("/categories")
def list_categories(request):
    return [{"name": c.name, "slug": c.slug, "friendly_name": c.friendly_name} for c in Category.objects.filter(is_active=True)]
