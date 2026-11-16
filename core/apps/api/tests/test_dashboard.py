import uuid
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductVariant
from apps.workspaces.models import Workspace, WorkspaceSettings


@pytest.fixture
def workspace(db):
    User = get_user_model()
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    # WorkspaceSettings создан сигналом — обновляем поля
    ws.settings.labor_mode = WorkspaceSettings.LaborMode.IGNORE_LABOR
    ws.settings.tax_rate = Decimal("4")
    ws.settings.equipment_hour_cost = Decimal("0")
    ws.settings.save()
    return ws


@pytest.mark.django_db
class TestTodayDashboard:
    def test_requires_workspace_id(self):
        client = APIClient()
        response = client.get("/api/v1/dashboard/today/")
        assert response.status_code == 400

    def test_empty_workspace(self, workspace):
        client = APIClient()
        response = client.get(f"/api/v1/dashboard/today/?workspace_id={workspace.id}")
        assert response.status_code == 200
        assert response.data["queued_jobs"] == []
        assert response.data["pending_promotions"] == []
        assert response.data["low_stocks"] == []
        assert response.data["unread_alerts"] == []


@pytest.mark.django_db
class TestVariantEconomics:
    def test_variant_without_recipe(self, workspace):
        p = Product.objects.create(workspace_id=workspace.id, name="X")
        v = ProductVariant.objects.create(product=p, name="Y")
        client = APIClient()
        response = client.get(
            f"/api/v1/dashboard/economics/?variant_id={v.id}&marketplace=wb&price=1000"
        )
        assert response.status_code == 200
        assert response.data["cost"] == "0.00"

    def test_variant_not_found(self):
        client = APIClient()
        response = client.get(
            f"/api/v1/dashboard/economics/?variant_id=99999"
        )
        assert response.status_code == 404
        

@pytest.mark.django_db
class TestCurrentWorkspace:
    def test_no_workspace_returns_404(self):
        client = APIClient()
        response = client.get("/api/v1/me/workspace/")
        assert response.status_code == 404

    def test_returns_first_workspace(self, workspace):
        client = APIClient()
        response = client.get("/api/v1/me/workspace/")
        assert response.status_code == 200
        assert response.data["id"] == str(workspace.id)
        assert response.data["name"] == "Мастерская"