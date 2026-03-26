"""Tests for orders app."""

import pytest
from decimal import Decimal
from django.test import Client
from apps.orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrderModel:
    def test_order_auto_generates_number(self, order):
        assert order.order_number is not None
        assert len(order.order_number) == 16

    def test_order_str(self, order):
        assert str(order) == order.order_number

    def test_order_default_status(self, order):
        assert order.status == Order.Status.PENDING

    def test_order_status_choices(self):
        assert Order.Status.CONFIRMED == "confirmed"
        assert Order.Status.SHIPPED == "shipped"
        assert Order.Status.CANCELLED == "cancelled"


@pytest.mark.django_db
class TestOrderItemModel:
    def test_order_item_calculates_line_total(self, order, product):
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            quantity=3,
            unit_price=Decimal(str(product.price)),
        )
        assert item.line_total == Decimal(str(product.price)) * 3

    def test_order_item_str(self, order, product):
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            quantity=1,
            unit_price=product.price,
        )
        assert product.name in str(item)


@pytest.mark.django_db
class TestOrderViews:
    def test_order_history_requires_login(self):
        client = Client()
        response = client.get("/orders/")
        assert response.status_code == 302  # Redirect to login

    def test_order_history_shows_orders(self, order, user):
        client = Client()
        client.force_login(user)
        response = client.get("/orders/")
        assert response.status_code == 200
        assert order.order_number in response.content.decode()

    def test_order_detail_requires_login(self):
        client = Client()
        response = client.get("/orders/SOME123/")
        assert response.status_code == 302

    def test_order_detail_shows_items(self, order, product):
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            quantity=2,
            unit_price=product.price,
        )
        client = Client()
        client.force_login(order.user)
        response = client.get(f"/orders/{order.order_number}/")
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_order_detail_404_for_other_user(self, order, user):
        from django.contrib.auth import get_user_model
        other = get_user_model().objects.create_user(username="other2", email="other2@x.com", password="x")
        client = Client()
        client.force_login(other)
        response = client.get(f"/orders/{order.order_number}/")
        assert response.status_code == 404
