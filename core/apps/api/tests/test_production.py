import uuid
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductVariant
from apps.production.models import ProductionJob
from apps.warehouse.models import Warehouse


@pytest.fixture
def variant(db):
    p = Product.objects.create(workspace_id=uuid.uuid4(), name="Органайзер")
    return ProductVariant.objects.create(product=p, name="Зелёный")


@pytest.mark.django_db
class TestProductionJobReportAPI:
    def test_report_success(self, variant):
        ws_id = uuid.uuid4()
        Warehouse.objects.create(
            workspace_id=ws_id, name="Склад", type=Warehouse.Type.OWN,
        )
        job = ProductionJob.objects.create(
            workspace_id=ws_id, variant=variant, qty_planned=10,
        )
        client = APIClient()
        response = client.post(
            f"/api/v1/jobs/{job.id}/report/",
            {"qty_done": 10, "qty_waste": 0, "actual_time_min": 45},
            format="json",
        )
        assert response.status_code == 200
        job.refresh_from_db()
        assert job.status == ProductionJob.Status.DONE

    def test_report_already_done_returns_400(self, variant):
        ws_id = uuid.uuid4()
        job = ProductionJob.objects.create(
            workspace_id=ws_id, variant=variant,
            status=ProductionJob.Status.DONE,
        )
        client = APIClient()
        response = client.post(
            f"/api/v1/jobs/{job.id}/report/",
            {"qty_done": 5}, format="json",
        )
        assert response.status_code == 400