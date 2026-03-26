"""Views for cart app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .models import Cart, CartItem
from apps.products.models import Product


def get_or_create_cart(request):
    """Get the current user's cart, creating if necessary."""

    if request.user.is_authenticated:
        return Cart.objects.get_or_create(user=request.user)[0]
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.get_or_create(session_key=request.session.session_key)[0]


@require_POST
def add_to_cart(request, product_id):
    """Add a product to the cart. Returns JSON for AJAX or redirects for normal."""

    product = get_object_or_404(Product, id=product_id, status=Product.Status.ACTIVE)
    cart = get_or_create_cart(request)

    size = request.POST.get("size", "").strip()
    quantity = int(request.POST.get("quantity", 1))
    quantity = max(1, min(quantity, 99))  # Clamp 1–99

    # Check stock — redirect with message if insufficient
    if product.stock < quantity:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Not enough stock. Only %d available." % product.stock}, status=400)
        messages.error(request, "Not enough stock. Only %d available." % product.stock)
        return redirect("products:product_detail", slug=product.slug)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, size=size,
        defaults={"quantity": quantity}
    )
    if not created:
        item.quantity = min(item.quantity + quantity, 99)
        item.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "item_count": cart.item_count,
            "grand_total": cart.grand_total,
        })

    messages.success(request, f"{product.name} added to cart.")
    return redirect("products:product_detail", slug=product.slug)


@require_POST
def update_cart(request, item_id):
    """Update quantity of a cart item."""

    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, 99)
        item.save()

    cart = item.cart
    return JsonResponse({
        "success": True,
        "item_count": cart.item_count,
        "subtotal": cart.subtotal,
        "delivery": cart.delivery_cost,
        "grand_total": cart.grand_total,
    })


@require_POST
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""

    item = get_object_or_404(CartItem, id=item_id)
    cart = item.cart
    item.delete()

    return JsonResponse({
        "success": True,
        "item_count": cart.item_count,
        "subtotal": cart.subtotal,
        "delivery": cart.delivery_cost,
        "grand_total": cart.grand_total,
    })


def view_cart(request):
    """Full cart page."""

    cart = get_or_create_cart(request)
    return render(request, "cart/cart.html", {"cart": cart})
