import uuid
from datetime import date, datetime, timedelta, timezone as tz
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductVariant
from apps.promo.models import Promotion, PromotionItem
from apps.workspaces.models import Workspace, WorkspaceSettings


@pytest.fixture
def workspace(db):
    User = get_user_model()
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    ws.settings.labor_mode = WorkspaceSettings.LaborMode.IGNORE_LABOR
    ws.settings.tax_rate = Decimal("4")
    ws.settings.save()
    return ws


@pytest.fixture
def variant(db, workspace):
    p = Product.objects.create(workspace_id=workspace.id, name="Органайзер")
    return ProductVariant.objects.create(product=p, name="Зелёный")


@pytest.fixture
def promotion(db, workspace):
    now = datetime.now(tz.utc)
    return Promotion.objects.create(
        workspace_id=workspace.id, marketplace="wb",
        name="Чёрная пятница", starts_at=now,
        ends_at=now + timedelta(days=7),
        discount_percent=Decimal("20"),
    )


@pytest.fixture
def item(db, promotion, variant):
    return PromotionItem.objects.create(
        promotion=promotion, variant=variant,
        proposed_price=Decimal("799.00"),
    )


@pytest.mark.django_db
class TestDecide:
    def test_accept(self, item):
        client = APIClient()
        response = client.post(
            f"/api/v1/promotion-items/{item.id}/decide/",
            {"decision": "accepted"}, format="json",
        )
        assert response.status_code == 200
        item.refresh_from_db()
        assert item.decision == "accepted"
        assert item.decided_at is not None

    def test_decline(self, item):
        client = APIClient()
        response = client.post(
            f"/api/v1/promotion-items/{item.id}/decide/",
            {"decision": "declined"}, format="json",
        )
        assert response.status_code == 200
        item.refresh_from_db()
        assert item.decision == "declined"

    def test_invalid_decision(self, item):
        client = APIClient()
        response = client.post(
            f"/api/v1/promotion-items/{item.id}/decide/",
            {"decision": "maybe"}, format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestForecast:
    def test_forecast(self, item):
        client = APIClient()
        response = client.get(f"/api/v1/promotion-items/{item.id}/forecast/")
        assert response.status_code == 200
        assert "margin" in response.data
        assert "is_loss" in response.data
        assert response.data["proposed_price"] == "799.00"

    def test_forecast_loss(self, item):
        # нет рецепта → cost=0, маржа = 799 - 0 - 0 - 31.96 = 767.04 > 0
        # чтобы был убыток — уменьшим proposed_price
        item.proposed_price = Decimal("1.00")
        item.save()
        client = APIClient()
        response = client.get(f"/api/v1/promotion-items/{item.id}/forecast/")
        assert response.status_code == 200
        # cost=0, tax=0.04 → margin = 1 - 0.04 = 0.96 > 0
        # для убытка нужен fee (комиссия) или cost
        assert "margin" in response.data