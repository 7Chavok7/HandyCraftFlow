# core/apps/warehouse/tests.py
import uuid
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Product, ProductVariant
from apps.warehouse.models import SellerAccount, Warehouse, Stock, StockLedger


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def variant(db, workspace_id):
    product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
    return ProductVariant.objects.create(product=product, name="Зелёный")


@pytest.fixture
def seller_account(db, workspace_id):
    return SellerAccount.objects.create(
        workspace_id=workspace_id, marketplace="wb", name="Основной WB",
    )


@pytest.fixture
def own_warehouse(db, workspace_id):
    return Warehouse.objects.create(
        workspace_id=workspace_id, name="Свой склад", type=Warehouse.Type.OWN,
    )


@pytest.fixture
def wb_warehouse(db, workspace_id, seller_account):
    return Warehouse.objects.create(
        workspace_id=workspace_id, name="WB FBO Коледино",
        type=Warehouse.Type.FBO, seller_account=seller_account,
    )


# --- SellerAccount ---

@pytest.mark.django_db
class TestSellerAccount:
    def test_str(self, seller_account):
        assert "Wildberries" in str(seller_account)
        assert "Основной WB" in str(seller_account)

    def test_unique_per_workspace_marketplace_name(self, workspace_id, seller_account):
        with pytest.raises(IntegrityError):
            SellerAccount.objects.create(
                workspace_id=workspace_id, marketplace="wb", name="Основной WB",
            )

    def test_default_is_active(self, workspace_id):
        acc = SellerAccount.objects.create(
            workspace_id=workspace_id, marketplace="ozon",
        )
        assert acc.is_active is True


# --- Warehouse ---

@pytest.mark.django_db
class TestWarehouse:
    def test_str(self, own_warehouse):
        assert "Свой склад" in str(own_warehouse)
        assert "Свой склад" in str(own_warehouse)  # type display

    def test_seller_account_optional(self, own_warehouse):
        assert own_warehouse.seller_account is None

    def test_seller_account_set(self, wb_warehouse, seller_account):
        assert wb_warehouse.seller_account == seller_account

    def test_unique_name_per_workspace(self, workspace_id, own_warehouse):
        with pytest.raises(IntegrityError):
            Warehouse.objects.create(
                workspace_id=workspace_id, name="Свой склад", type=Warehouse.Type.OWN,
            )


# --- Stock ---

@pytest.mark.django_db
class TestStock:
    def test_str(self, variant, own_warehouse):
        s = Stock.objects.create(variant=variant, warehouse=own_warehouse, qty=Decimal("10"))
        assert "10" in str(s)

    def test_available_qty(self, variant, own_warehouse):
        s = Stock.objects.create(
            variant=variant, warehouse=own_warehouse,
            qty=Decimal("10"), reserved_qty=Decimal("3"),
        )
        assert s.available_qty == Decimal("7")

    def test_available_qty_zero_reserve(self, variant, own_warehouse):
        s = Stock.objects.create(
            variant=variant, warehouse=own_warehouse, qty=Decimal("10"),
        )
        assert s.available_qty == Decimal("10")

    def test_unique_variant_warehouse(self, variant, own_warehouse):
        Stock.objects.create(variant=variant, warehouse=own_warehouse)
        with pytest.raises(IntegrityError):
            Stock.objects.create(variant=variant, warehouse=own_warehouse)


# --- StockLedger ---

@pytest.mark.django_db
class TestStockLedger:
    def test_str_positive(self, variant, own_warehouse):
        entry = StockLedger.objects.create(
            variant=variant, warehouse=own_warehouse,
            movement_type=StockLedger.MovementType.PRODUCTION_IN,
            qty=Decimal("10"),
        )
        assert "+10" in str(entry)
        assert "Поступление из производства" in str(entry)

    def test_str_negative(self, variant, own_warehouse):
        entry = StockLedger.objects.create(
            variant=variant, warehouse=own_warehouse,
            movement_type=StockLedger.MovementType.SALE,
            qty=Decimal("-2"),
        )
        assert "-2" in str(entry)
        assert "Продажа" in str(entry)

    def test_reserve_zero_qty(self, variant, own_warehouse):
        # резерв: qty=0, изменяется только reserved_qty
        entry = StockLedger.objects.create(
            variant=variant, warehouse=own_warehouse,
            movement_type=StockLedger.MovementType.RESERVE,
            qty=Decimal("0"), comment="резерв под заказ WB #123",
        )
        assert entry.qty == Decimal("0")
        assert "Резерв" in str(entry)

    def test_movement_types_exist(self):
        assert StockLedger.MovementType.RESERVE.value == "reserve"
        assert StockLedger.MovementType.UNRESERVE.value == "unreserve"