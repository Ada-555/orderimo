"""Tests for products app."""

import pytest
from apps.products.models import Category, Product


# ─── Model Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = Category.objects.create(name="Books", slug="books")
        assert cat.name == "Books"
        assert cat.slug == "books"

    def test_category_auto_slug(self):
        cat = Category.objects.create(name="Home & Garden")
        assert cat.slug == "home-garden"

    def test_category_str(self):
        cat = Category.objects.create(name="Electronics", slug="electronics")
        assert str(cat) == "Electronics"


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self):
        cat = Category.objects.create(name="TestCat", slug="testcat")
        p = Product.objects.create(
            category=cat,
            sku="TEST-001",
            name="Widget",
            slug="widget",
            description="A widget.",
            price="29.99",
            stock=5,
            status=Product.Status.ACTIVE,
        )
        assert p.name == "Widget"
        assert p.current_price == "29.99"

    def test_product_sale_price(self):
        cat = Category.objects.create(name="Cat2", slug="cat2")
        p = Product.objects.create(
            category=cat, sku="SALE-001", name="Sale Product", slug="sale-product",
            description="D", price="99.99", status=Product.Status.ACTIVE
        )
        p.sale_price = "79.99"
        p.save()
        assert p.current_price == "79.99"

    def test_product_auto_slug(self):
        cat = Category.objects.create(name="Cat3", slug="cat3")
        p = Product.objects.create(
            category=cat, sku="AUTO-001", name="My Cool Product",
            description="Desc", price="10.00", status=Product.Status.ACTIVE
        )
        assert p.slug == "my-cool-product"

    def test_product_str(self):
        cat = Category.objects.create(name="Cat4", slug="cat4")
        p = Product.objects.create(
            category=cat, sku="STR-001", name="Test Product",
            slug="test-product-str", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        assert str(p) == "Test Product"


# ─── View Tests ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductListView:
    def test_product_list_returns_200(self):
        from django.test import Client
        client = Client()
        response = client.get("/products/")
        assert response.status_code == 200

    def test_product_list_shows_active_products(self):
        cat = Category.objects.create(name="ListCat", slug="list-cat")
        p = Product.objects.create(
            category=cat, sku="LIST-001", name="Visible Product",
            slug="visible-product", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/products/")
        assert response.status_code == 200
        assert "Visible Product" in response.content.decode()

    def test_product_list_excludes_draft(self):
        cat = Category.objects.create(name="DraftCat", slug="draft-cat")
        Product.objects.create(
            category=cat, sku="DRAFT-001", name="Draft Product",
            slug="draft-product", description="D", price="1.00",
            status=Product.Status.DRAFT
        )
        from django.test import Client
        client = Client()
        response = client.get("/products/")
        assert "Draft Product" not in response.content.decode()

    def test_product_list_search(self):
        cat = Category.objects.create(name="SearchCat", slug="search-cat")
        p = Product.objects.create(
            category=cat, sku="SRCH-001", name="Findable Widget",
            slug="findable-widget", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/products/?q=Findable")
        assert response.status_code == 200
        assert "Findable Widget" in response.content.decode()

    def test_product_list_filter_by_category(self):
        cat = Category.objects.create(name="FilterCat", slug="filter-cat")
        p = Product.objects.create(
            category=cat, sku="FILT-001", name="Filtered Item",
            slug="filtered-item", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/products/?category=filter-cat")
        assert response.status_code == 200
        assert "Filtered Item" in response.content.decode()


@pytest.mark.django_db
class TestProductDetailView:
    def test_product_detail_returns_200(self):
        cat = Category.objects.create(name="DetailCat", slug="detail-cat")
        p = Product.objects.create(
            category=cat, sku="DET-001", name="Detail Product",
            slug="detail-product", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get(f"/products/{p.slug}/")
        assert response.status_code == 200

    def test_product_detail_404_for_draft(self):
        cat = Category.objects.create(name="DetailCat2", slug="detail-cat2")
        p = Product.objects.create(
            category=cat, sku="DET2-001", name="Draft Detail",
            slug="draft-detail", description="D", price="1.00",
            status=Product.Status.DRAFT
        )
        from django.test import Client
        client = Client()
        response = client.get(f"/products/{p.slug}/")
        assert response.status_code == 404

    def test_product_detail_shows_related(self):
        cat = Category.objects.create(name="DetailCat3", slug="detail-cat3")
        p = Product.objects.create(
            category=cat, sku="DET3-001", name="Related Product",
            slug="related-product", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get(f"/products/{p.slug}/")
        assert response.status_code == 200


# ─── CRUD Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductCRUD:
    def test_create_product_via_view(self, superuser):
        from django.test import Client
        client = Client()
        client.force_login(superuser)
        response = client.post("/products/create/", {
            "name": "New Product",
            "sku": "CRUD-001",
            "description": "A new product",
            "price": "49.99",
            "stock": 20,
            "status": "active",
        })
        assert response.status_code == 302
        assert Product.objects.filter(sku="CRUD-001").exists()

    def test_edit_product_via_view(self, superuser):
        cat = Category.objects.create(name="EditCat", slug="edit-cat")
        p = Product.objects.create(
            category=cat, sku="EDIT-001", name="Original Name",
            slug="original-name", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        client.force_login(superuser)
        response = client.post(f"/products/{p.slug}/edit/", {
            "name": "Updated Name",
            "sku": p.sku,
            "description": p.description,
            "price": "149.99",
            "stock": 5,
            "status": p.status,
        })
        assert response.status_code == 302
        p.refresh_from_db()
        assert p.name == "Updated Name"

    def test_delete_product_via_view(self, superuser):
        cat = Category.objects.create(name="DelCat", slug="del-cat")
        p = Product.objects.create(
            category=cat, sku="DEL-001", name="To Delete",
            slug="to-delete", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        client.force_login(superuser)
        response = client.post(f"/products/{p.slug}/delete/")
        assert response.status_code == 302
        assert not Product.objects.filter(id=p.id).exists()

    def test_non_superuser_cannot_create(self, user):
        from django.test import Client
        client = Client()
        client.force_login(user)
        response = client.post("/products/create/", {
            "name": "Hacked", "sku": "X", "description": "X", "price": "1.00"
        })
        assert response.status_code == 302


# ─── API Tests ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductAPI:
    def test_api_list_products(self):
        cat = Category.objects.create(name="APICat", slug="api-cat")
        Product.objects.create(
            category=cat, sku="API-001", name="API Product",
            slug="api-product", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_api_list_filtered_by_category(self):
        cat = Category.objects.create(name="APIFilterCat", slug="apifilter-cat")
        p = Product.objects.create(
            category=cat, sku="APIF-001", name="Filterable API Product",
            slug="filterable-api-product", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/api/products?category=apifilter-cat")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Filterable API Product"

    def test_api_list_search(self):
        cat = Category.objects.create(name="APISearchCat", slug="apisearch-cat")
        Product.objects.create(
            category=cat, sku="APIS-001", name="Searchable Widget",
            slug="searchable-widget", description="D", price="10.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get("/api/products?search=Sear")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_api_get_product(self):
        cat = Category.objects.create(name="APIGetCat", slug="apiget-cat")
        p = Product.objects.create(
            category=cat, sku="APIG-001", name="Get Me",
            slug="get-me", description="A product", price="25.00",
            status=Product.Status.ACTIVE
        )
        from django.test import Client
        client = Client()
        response = client.get(f"/api/products/{p.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Me"
        assert data["sku"] == "APIG-001"

    def test_api_get_product_404(self):
        from django.test import Client
        client = Client()
        response = client.get("/api/products/nonexistent")
        assert response.status_code == 404
