import uuid
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.workspaces.models import Workspace, WorkspaceSettings

User = get_user_model()


@pytest.fixture
def workspace(db):
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    ws.settings.labor_mode = WorkspaceSettings.LaborMode.MANUAL_RATE
    ws.settings.labor_rate = Decimal("500")
    ws.settings.tax_rate = Decimal("4")
    ws.settings.save()
    return ws


@pytest.mark.django_db
class TestSettingsAPI:
    def test_list(self, workspace):
        client = APIClient()
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["labor_mode"] == "manual_rate"

    def test_current(self, workspace):
        client = APIClient()
        response = client.get("/api/v1/settings/current/")
        assert response.status_code == 200
        assert response.data["workspace_name"] == "Мастерская"
        assert response.data["labor_rate"] == "500.00"

    def test_update(self, workspace):
        settings = workspace.settings
        client = APIClient()
        response = client.patch(
            f"/api/v1/settings/{settings.id}/",
            {"tax_rate": "6.00"},
            format="json",
        )
        assert response.status_code == 200
        settings.refresh_from_db()
        assert settings.tax_rate == Decimal("6.00")

    def test_effective_labor_rate_manual(self, workspace):
        client = APIClient()
        response = client.get("/api/v1/settings/current/")
        assert response.data["effective_labor_rate"] == "500.00"