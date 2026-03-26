"""Checkout views — Stripe payment intent + order creation."""

import json
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from allauth.account.decorators import verified_email_required

from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem
from .forms import CheckoutForm


def _get_cart(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).first()
    if request.session.session_key:
        return Cart.objects.filter(session_key=request.session.session_key).first()
    return None


def checkout(request):
    cart = _get_cart(request)
    if not cart or cart.item_count == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:view_cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create Stripe PaymentIntent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(cart.grand_total * 100),
                    currency=settings.STRIPE_CURRENCY,
                    automatic_payment_methods={"enabled": True},
                    metadata={
                        "user_id": request.user.id if request.user.is_authenticated else "",
                        "session_key": request.session.session_key or "",
                    },
                )
            except stripe.error.StripeError as e:
                messages.error(request, f"Payment setup failed: {e}")
                return render(request, "checkout/checkout.html", {
                    "form": form, "cart": cart,
                    "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
                })

            # Build order (pending payment)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data.get("phone", ""),
                address_line1=form.cleaned_data["address_line1"],
                address_line2=form.cleaned_data.get("address_line2", ""),
                city=form.cleaned_data["city"],
                county=form.cleaned_data.get("county", ""),
                postcode=form.cleaned_data.get("postcode", ""),
                country=form.cleaned_data["country"],
                subtotal=cart.subtotal,
                delivery_cost=cart.delivery_cost,
                grand_total=cart.grand_total,
                stripe_pid=intent.id,
            )

            # Create order items from cart
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    size=item.size,
                    quantity=item.quantity,
                    unit_price=item.product.current_price,
                    line_total=item.subtotal,
                )

            return render(request, "checkout/payment.html", {
                "order": order,
                "client_secret": intent.client_secret,
                "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            })
    else:
        form = CheckoutForm()

    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart": cart,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


@require_POST
def payment_success(request):
    """Called after Stripe confirms payment."""

    data = json.loads(request.body)
    pid = data.get("payment_intent")

    order = Order.objects.filter(stripe_pid=pid).first()
    if not order:
        return redirect("products:product_list")

    order.status = Order.Status.CONFIRMED
    order.save()

    # Clear cart
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).delete()
    elif request.session.session_key:
        Cart.objects.filter(session_key=request.session.session_key).delete()

    messages.success(request, f"Order {order.order_number} confirmed! Thank you.")
    return render(request, "checkout/success.html", {"order": order})
