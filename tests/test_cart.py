"""Tests for cart app."""

import pytest
from django.test import Client
from apps.cart.models import Cart, CartItem
from apps.products.models import Product


@pytest.mark.django_db
class TestCartModel:
    def test_cart_created_for_user(self, user):
        cart = Cart.objects.create(user=user)
        assert cart.user == user

    def test_cart_item_count(self, cart, cart_item):
        assert cart.item_count == 2

    def test_cart_subtotal(self, cart, cart_item, product):
        # cart_item has quantity=2, product price=99.99
        expected = float(product.price) * 2
        assert cart.subtotal == expected

    def test_cart_grand_total_includes_delivery(self, cart, cart_item, product):
        # Cart subtotal = 99.99 * 2 = 199.98 which is > 80 (free threshold)
        assert cart.grand_total == cart.subtotal  # Free delivery

    def test_cart_item_unique_together(self, cart, product):
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        # Trying to create another with same cart/product/size should fail
        with pytest.raises(Exception):  # IntegrityError
            CartItem.objects.create(cart=cart, product=product, quantity=1)

    def test_cart_item_with_size(self, cart, product):
        item = CartItem.objects.create(cart=cart, product=product, size="M", quantity=1)
        assert item.size == "M"
        assert item.subtotal == float(product.price)


@pytest.mark.django_db
class TestCartViews:
    def test_view_cart_empty(self, user):
        client = Client()
        if user.is_authenticated:
            client.force_login(user)
        response = client.get("/cart/")
        assert response.status_code == 200

    def test_view_cart_with_items(self, cart, cart_item):
        client = Client()
        client.force_login(cart.user)
        response = client.get("/cart/")
        assert response.status_code == 200

    def test_add_to_cart_ajax(self, product, user):
        client = Client()
        client.force_login(user)
        response = client.post(
            f"/cart/add/{product.id}/",
            {"quantity": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_add_to_cart_redirect(self, product, user):
        client = Client()
        client.force_login(user)
        response = client.post(f"/cart/add/{product.id}/", {"quantity": 1})
        assert response.status_code == 302

    def test_add_invalid_product_returns_404(self, user):
        client = Client()
        client.force_login(user)
        response = client.post("/cart/add/99999/")
        assert response.status_code == 404

    def test_update_cart_item(self, cart_item):
        client = Client()
        client.force_login(cart_item.cart.user)
        response = client.post(
            f"/cart/update/{cart_item.id}/",
            {"quantity": 5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        cart_item.refresh_from_db()
        assert cart_item.quantity == 5

    def test_update_cart_item_to_zero_deletes(self, cart_item):
        client = Client()
        client.force_login(cart_item.cart.user)
        response = client.post(
            f"/cart/update/{cart_item.id}/",
            {"quantity": 0},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        assert not CartItem.objects.filter(id=cart_item.id).exists()

    def test_remove_cart_item(self, cart_item):
        client = Client()
        client.force_login(cart_item.cart.user)
        response = client.post(
            f"/cart/remove/{cart_item.id}/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        assert not CartItem.objects.filter(id=cart_item.id).exists()
