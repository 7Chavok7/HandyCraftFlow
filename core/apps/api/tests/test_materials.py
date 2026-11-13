import uuid
from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.guide.models import Unit
from apps.materials.models import MaterialType, MaterialBatch


@pytest.fixture
def unit_gram(db):
    return Unit.objects.create(name="Грамм", short_name="г")


@pytest.fixture
def material_type(db, unit_gram):
    return MaterialType.objects.create(
        workspace_id=uuid.uuid4(), name="PLA", unit=unit_gram,
    )


@pytest.mark.django_db
class TestMaterialTypeAPI:
    def test_list(self, material_type):
        client = APIClient()
        response = client.get("/api/v1/materials/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "PLA"


@pytest.mark.django_db
class TestMaterialBatchAPI:
    def test_list(self, material_type):
        MaterialBatch.objects.create(
            material_type=material_type,
            qty_initial=Decimal("1000"), qty_remaining=Decimal("1000"),
            unit_cost=Decimal("1"), purchased_at=date(2025, 1, 1),
        )
        client = APIClient()
        response = client.get("/api/v1/batches/")
        assert response.status_code == 200
        assert response.data["count"] == 1