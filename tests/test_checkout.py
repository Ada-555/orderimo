"""Tests for checkout app."""

import pytest
from django.test import Client
from apps.cart.models import Cart, CartItem
from apps.checkout.forms import CheckoutForm


@pytest.mark.django_db
class TestCheckoutForm:
    def test_checkout_form_valid(self):
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+123456789",
            "address_line1": "123 Main St",
            "city": "Dublin",
            "country": "IE",
        }
        form = CheckoutForm(data)
        assert form.is_valid(), form.errors

    def test_checkout_form_missing_required(self):
        form = CheckoutForm({})
        assert not form.is_valid()
        assert "full_name" in form.errors
        assert "email" in form.errors
        assert "address_line1" in form.errors
        assert "city" in form.errors
        assert "country" in form.errors

    def test_checkout_form_invalid_email(self):
        data = {
            "full_name": "Test",
            "email": "not-an-email",
            "address_line1": "123 Main",
            "city": "Dublin",
            "country": "IE",
        }
        form = CheckoutForm(data)
        assert not form.is_valid()
        assert "email" in form.errors


@pytest.mark.django_db
class TestCheckoutViews:
    def test_checkout_empty_cart_redirects(self, user):
        client = Client()
        client.force_login(user)
        response = client.get("/checkout/")
        assert response.status_code == 302

    def test_checkout_with_cart(self, cart, cart_item, user):
        client = Client()
        client.force_login(user)
        response = client.get("/checkout/")
        assert response.status_code == 200

    def test_checkout_success_requires_post(self, order):
        client = Client()
        response = client.get("/checkout/success/")
        # checkout success requires POST (@require_POST)
        assert response.status_code == 405
