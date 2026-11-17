import uuid
import pytest

from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.catalog.models import Product, ProductVariant
from apps.workspaces.models import Workspace, WorkspaceSettings


User = get_user_model()

@pytest.fixture
def workspace(db):
    User = get_user_model()
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    ws.settings.labor_mode = WorkspaceSettings.LaborMode.IGNORE_LABOR
    ws.settings.tax_rate = Decimal("4")
    ws.settings.equipment_hour_cost = Decimal("0")
    ws.settings.save()
    return ws

@pytest.fixture
def variant(db, workspace):
    p = Product.objects.create(workspace_id=workspace.id, name="Органайзер")
    return ProductVariant.objects.create(product=p, name="Зелёный")


@pytest.mark.django_db
class TestProductsAPI:
    def test_list_with_variants(self, workspace):
        p = Product.objects.create(workspace_id=workspace.id, name="Органайзер")
        ProductVariant.objects.create(product=p, name="Зелёный")
        client = APIClient()
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        results = response.data["results"]
        assert results[0]["name"] == "Органайзер"
        assert len(results[0]["variants"]) == 1
        
        
@pytest.mark.django_db
class TestVariantDetailAPI:
    def test_detail_without_recipe(self, variant):
        client = APIClient()
        response = client.get(f"/api/v1/variants/{variant.id}/detail/")
        assert response.status_code == 200
        assert response.data["recipe"] is None
        assert response.data["stocks"] == []
        assert response.data["economics"]["cost"] == "0.00"

    def test_detail_with_stocks(self, variant, workspace):
        from apps.warehouse.models import Warehouse, Stock
        wh = Warehouse.objects.create(
            workspace_id=workspace.id, name="Склад", type=Warehouse.Type.OWN,
        )
        Stock.objects.create(variant=variant, warehouse=wh, qty=Decimal("5"))
        client = APIClient()
        response = client.get(f"/api/v1/variants/{variant.id}/detail/")
        assert response.status_code == 200
        assert len(response.data["stocks"]) == 1
        
    def test_detail_returns_all_variants(self, variant):
        ProductVariant.objects.create(product=variant.product, name="Красный")
        client = APIClient()
        response = client.get(f"/api/v1/variants/{variant.id}/detail/")
        assert response.status_code == 200
        assert len(response.data["all_variants"]) == 2
        
        
@pytest.mark.django_db
class TestProductCRUD:
    def test_create_product(self, workspace):
        client = APIClient()
        response = client.post("/api/v1/products/", {
            "workspace_id": str(workspace.id),
            "name": "Новый товар",
            "description": "тест",
            "is_active": True,
        }, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "Новый товар"

    def test_update_product(self, workspace):
        from apps.catalog.models import Product
        p = Product.objects.create(workspace_id=workspace.id, name="Старый")
        client = APIClient()
        response = client.patch(
            f"/api/v1/products/{p.id}/", {"name": "Новый"}, format="json",
        )
        assert response.status_code == 200
        p.refresh_from_db()
        assert p.name == "Новый"

    def test_delete_product(self, workspace):
        from apps.catalog.models import Product
        p = Product.objects.create(workspace_id=workspace.id, name="Удалить")
        client = APIClient()
        response = client.delete(f"/api/v1/products/{p.id}/")
        assert response.status_code == 204
        
        
@pytest.mark.django_db
class TestVariantCRUD:
    def test_create_variant(self, workspace, variant):
        client = APIClient()
        response = client.post("/api/v1/variants/", {
            "product": variant.product.id,
            "name": "Красный",
            "extra_cost": "5.00",
            "is_active": True,
        }, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "Красный"

    def test_update_variant(self, variant):
        client = APIClient()
        response = client.patch(
            f"/api/v1/variants/{variant.id}/",
            {"name": "Тёмно-зелёный"},
            format="json",
        )
        assert response.status_code == 200
        variant.refresh_from_db()
        assert variant.name == "Тёмно-зелёный"

    def test_delete_variant(self, variant):
        client = APIClient()
        response = client.delete(f"/api/v1/variants/{variant.id}/")
        assert response.status_code == 204
        
    def test_variant_has_product_name(self, variant):
        client = APIClient()
        response = client.get(f"/api/v1/variants/{variant.id}/")
        assert response.data["product_name"] == "Органайзер"