import uuid

import pytest
from rest_framework.test import APIClient

from apps.warehouse.models import Warehouse


@pytest.mark.django_db
class TestWarehouseAPI:
    def test_list(self):
        Warehouse.objects.create(
            workspace_id=uuid.uuid4(), name="Свой склад", type=Warehouse.Type.OWN,
        )
        client = APIClient()
        response = client.get("/api/v1/warehouses/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_create(self):
        client = APIClient()
        response = client.post("/api/v1/warehouses/", {
            "workspace_id": str(uuid.uuid4()),
            "name": "Новый склад",
            "type": "own",
        })
        assert response.status_code == 201