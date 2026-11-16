import uuid
import pytest

from decimal import Decimal
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
        
        
@pytest.mark.django_db
class TestStockActionsAPI:
    def _setup(self):
        import uuid
        from apps.catalog.models import Product, ProductVariant
        ws = uuid.uuid4()
        p = Product.objects.create(workspace_id=ws, name="X")
        v = ProductVariant.objects.create(product=p, name="Y")
        wh = Warehouse.objects.create(
            workspace_id=ws, name="Склад", type=Warehouse.Type.OWN,
        )
        from apps.warehouse.models import Stock
        stock = Stock.objects.create(variant=v, warehouse=wh, qty=Decimal("10"))
        return stock

    def test_adjust(self):
        from apps.warehouse.models import Stock
        stock = self._setup()
        client = APIClient()
        response = client.post(
            f"/api/v1/stocks/{stock.id}/adjust/",
            {"new_qty": "15", "comment": "нашёл"}, format="json",
        )
        assert response.status_code == 200
        stock.refresh_from_db()
        assert stock.qty == Decimal("15")

    def test_reserve(self):
        stock = self._setup()
        client = APIClient()
        response = client.post(
            f"/api/v1/stocks/{stock.id}/reserve/",
            {"qty": "3"}, format="json",
        )
        assert response.status_code == 200
        stock.refresh_from_db()
        assert stock.reserved_qty == Decimal("3")

    def test_unreserve(self):
        stock = self._setup()
        stock.reserved_qty = Decimal("5")
        stock.save()
        client = APIClient()
        response = client.post(
            f"/api/v1/stocks/{stock.id}/unreserve/",
            {"qty": "2"}, format="json",
        )
        assert response.status_code == 200
        stock.refresh_from_db()
        assert stock.reserved_qty == Decimal("3")