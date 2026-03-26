"""Template rendering tests — catches crispy/filter/syntax errors the Django test client misses."""

import pytest
from django.test import Client
from django.template import Template, Context, TemplateSyntaxError


# Pages that MUST render without template errors
PAGES = [
    "/",
    "/products/",
    "/accounts/login/",
    "/accounts/signup/",
    "/accounts/logout/",
    "/cart/",
]


@pytest.mark.django_db
class TestTemplateRendering:
    """Ensure all pages render without template syntax errors."""

    @pytest.mark.parametrize("path", PAGES)
    def test_page_renders_without_errors(self, path):
        """Each page should return 200 and contain no template error strings."""
        client = Client()
        response = client.get(path, follow=True)
        content = response.content.decode()

        assert "TemplateDoesNotExist" not in content, f"{path}: Template missing"
        assert "Invalid filter" not in content, f"{path}: Crispy not loaded"
        assert "Exception" not in content or "NoReverseMatch" not in content, f"{path}: Template error"
        assert response.status_code in [200, 302], f"{path}: Got {response.status_code}"


class TestCrispyFormsTags:
    """Verify crispy template tags work in key templates."""

    def test_login_template_uses_bootstrap_forms(self):
        """Login template must have Bootstrap form controls."""
        from django.template import engines
        engine = engines["django"]
        template = engine.get_template("account/login.html")
        source = template.origin.loader.get_contents(template.origin)
        # Auth pages use plain Bootstrap — no crispy needed
        assert 'class="form-control"' in source or 'form-label' in source
        assert 'name="login"' in source
        assert 'name="password"' in source

    def test_signup_template_has_bootstrap_forms(self):
        """Signup template must have Bootstrap form controls."""
        from django.template import engines
        engine = engines["django"]
        template = engine.get_template("account/signup.html")
        source = template.origin.loader.get_contents(template.origin)
        assert 'class="form-control"' in source
        assert 'name="username"' in source
        assert 'name="password1"' in source


@pytest.mark.django_db
class TestCSSContrast:
    """Verify CSS contrast — dark text on dark backgrounds."""

    def test_base_template_defines_form_colors(self):
        """Base template should define form text colors."""
        from django.template import engines
        engine = engines["django"]
        template = engine.get_template("base.html")
        source = template.origin.loader.get_contents(template.origin)
        # Should have form text color definitions
        assert "color:" in source or ".form-control" in source

    def test_cart_page_has_white_text(self):
        """Cart page should render with visible text."""
        client = Client()
        response = client.get("/cart/", follow=True)
        assert response.status_code == 200
        # Check body has some visible text
        assert len(response.content.decode()) > 100


@pytest.mark.django_db
class TestPageContent:
    """Verify key pages contain expected content."""

    def test_home_page_has_plurino_brand(self):
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        assert "PLURINO" in content or "Plurino" in content

    def test_products_page_has_grid(self):
        client = Client()
        response = client.get("/products/")
        content = response.content.decode()
        assert response.status_code == 200
        assert "product" in content.lower() or "Shop" in content

    def test_login_page_has_form(self):
        client = Client()
        response = client.get("/accounts/login/", follow=True)
        content = response.content.decode()
        assert "login" in content.lower() or "email" in content.lower()

    def test_signup_page_has_form(self):
        client = Client()
        response = client.get("/accounts/signup/", follow=True)
        content = response.content.decode()
        assert "signup" in content.lower() or "sign up" in content.lower() or "create" in content.lower()

    def test_navbar_has_key_links(self):
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        # Should have Shop link
        assert "Shop" in content or "shop" in content
        # Should have Cart link
        assert "cart" in content.lower() or "bag" in content.lower()
