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
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    WorkspaceSettings.objects.create(
        workspace=ws,
        labor_mode=WorkspaceSettings.LaborMode.IGNORE_LABOR,
        tax_rate=Decimal("4"),
        equipment_hour_cost=Decimal("0"),
    )
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