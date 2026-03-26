"""Pytest fixtures — relies on pytest-django's built-in db fixture."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Electronics", slug="electronics", friendly_name="Electronics"
    )


@pytest.fixture
def product(db, category):
    import uuid
    unique = uuid.uuid4().hex[:6]
    return Product.objects.create(
        category=category,
        sku=f"ELEC-{unique}",
        name="Test Product",
        slug=f"test-product-{unique}",
        description="A test product description.",
        price=Decimal("99.99"),
        stock=10,
        status=Product.Status.ACTIVE,
    )


@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)


@pytest.fixture
def cart_item(db, cart, product):
    return CartItem.objects.create(cart=cart, product=product, quantity=2)


@pytest.fixture
def order(db, user):
    return Order.objects.create(
        user=user,
        full_name="Test User",
        email="test@example.com",
        phone="+1234567890",
        address_line1="123 Test Street",
        city="Dublin",
        county="Dublin",
        postcode="D01 AB12",
        country="IE",
        subtotal=Decimal("99.99"),
        delivery_cost=Decimal("0.00"),
        grand_total=Decimal("99.99"),
        status=Order.Status.PENDING,
    )
