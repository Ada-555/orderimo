"""Tests for accounts app."""

import pytest
from django.test import Client
from apps.accounts.models import User, Address


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass123"
        )
        assert user.email == "alice@example.com"
        assert user.check_password("pass123")

    def test_user_str(self, user):
        assert str(user) == user.email

    def test_user_is_not_verified_by_default(self):
        user = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass"
        )
        assert user.is_verified is False


@pytest.mark.django_db
class TestAddressModel:
    def test_create_address(self, user):
        addr = Address.objects.create(
            user=user,
            name="Home",
            line1="123 Main St",
            city="Dublin",
            country="IE",
            is_default=True,
        )
        assert addr.name == "Home"
        assert addr.is_default is True
        assert str(addr) == "Home — Dublin"

    def test_address_ordering(self, user):
        a1 = Address.objects.create(user=user, name="First", line1="1", city="D", country="IE")
        a2 = Address.objects.create(user=user, name="Second Default", line1="2", city="D", country="IE", is_default=True)
        a3 = Address.objects.create(user=user, name="Third", line1="3", city="D", country="IE")
        # Default should be first
        assert list(Address.objects.filter(user=user))[0].name == "Second Default"


@pytest.mark.django_db
class TestAccountViews:
    def test_signup_page_loads(self):
        client = Client()
        response = client.get("/accounts/signup/")
        assert response.status_code == 200

    def test_signup_creates_user(self):
        client = Client()
        response = client.post("/accounts/signup/", {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "complexpassword123!",
            "password2": "complexpassword123!",
        })
        assert response.status_code == 302
        assert User.objects.filter(email="new@example.com").exists()

    def test_address_list_requires_login(self):
        client = Client()
        response = client.get("/accounts/addresses/")
        assert response.status_code == 302

    def test_address_list_loads(self, user):
        client = Client()
        client.force_login(user)
        response = client.get("/accounts/addresses/")
        assert response.status_code == 200

    def test_address_create(self, user):
        client = Client()
        client.force_login(user)
        response = client.post("/accounts/addresses/create/", {
            "name": "Work",
            "line1": "456 Office Rd",
            "city": "Cork",
            "country": "IE",
        })
        assert response.status_code == 302
        assert Address.objects.filter(user=user, name="Work").exists()

    def test_address_edit(self, user):
        addr = Address.objects.create(
            user=user, name="Old Name", line1="1", city="D", country="IE"
        )
        client = Client()
        client.force_login(user)
        response = client.post(f"/accounts/addresses/{addr.pk}/edit/", {
            "name": "New Name",
            "line1": "1",
            "city": "D",
            "country": "IE",
        })
        assert response.status_code == 302
        addr.refresh_from_db()
        assert addr.name == "New Name"

    def test_address_delete(self, user):
        addr = Address.objects.create(
            user=user, name="Delete Me", line1="1", city="D", country="IE"
        )
        client = Client()
        client.force_login(user)
        response = client.post(f"/accounts/addresses/{addr.pk}/delete/")
        assert response.status_code == 302
        assert not Address.objects.filter(id=addr.id).exists()

    def test_cannot_delete_other_users_address(self, user):
        from django.contrib.auth import get_user_model
        other = get_user_model().objects.create_user(username="other", email="o@o.com", password="x")
        addr = Address.objects.create(
            user=other, name="Private", line1="1", city="D", country="IE"
        )
        client = Client()
        client.force_login(user)
        response = client.post(f"/accounts/addresses/{addr.pk}/delete/")
        assert response.status_code == 404
        assert Address.objects.filter(id=addr.id).exists()
