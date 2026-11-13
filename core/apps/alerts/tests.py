import uuid
from datetime import date
from decimal import Decimal

import pytest

from apps.alerts.models import Alert
from apps.alerts.services import create_alert
from apps.alerts import tasks
from apps.catalog.models import Product, ProductVariant
from apps.guide.models import Unit
from apps.materials.models import MaterialType, MaterialBatch
from apps.warehouse.models import Warehouse, Stock


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def unit_gram(db):
    return Unit.objects.create(name="Грамм", short_name="г")


# --- Alert model ---

@pytest.mark.django_db
class TestAlertModel:
    def test_str(self, workspace_id):
        a = Alert.objects.create(
            workspace_id=workspace_id, type=Alert.Type.MATERIAL_LOW,
            severity=Alert.Severity.WARNING, title="Мало PLA",
        )
        assert "Внимание" in str(a)
        assert "Мало PLA" in str(a)

    def test_default_is_read_false(self, workspace_id):
        a = Alert.objects.create(
            workspace_id=workspace_id, type=Alert.Type.STOCK_LOW,
            title="X",
        )
        assert a.is_read is False

    def test_related_object_optional(self, workspace_id):
        a = Alert.objects.create(
            workspace_id=workspace_id, type=Alert.Type.SYNC_FAILED, title="X",
        )
        assert a.related_object_id is None


# --- create_alert service ---

@pytest.mark.django_db
class TestCreateAlert:
    def test_default_severity_by_type(self, workspace_id):
        a = create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.MATERIAL_LOW,
            title="Мало PLA",
        )
        assert a.severity == Alert.Severity.WARNING

    def test_default_severity_critical(self, workspace_id):
        a = create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.SYNC_FAILED,
            title="Sync failed",
        )
        assert a.severity == Alert.Severity.CRITICAL

    def test_explicit_severity(self, workspace_id):
        a = create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.MATERIAL_LOW,
            title="X",
            severity=Alert.Severity.CRITICAL,
        )
        assert a.severity == Alert.Severity.CRITICAL

    def test_info_by_default(self, workspace_id):
        a = create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.PROMOTION_INCOMING,
            title="X",
        )
        assert a.severity == Alert.Severity.INFO

    def test_related_object_id_passed(self, workspace_id):
        obj_id = uuid.uuid4()
        a = create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.STOCK_LOW,
            title="X",
            related_object_id=obj_id,
        )
        assert a.related_object_id == obj_id


# --- Tasks ---

@pytest.mark.django_db
class TestCheckMaterialLow:
    def test_creates_alert_when_low(self, workspace_id, unit_gram):
        mt = MaterialType.objects.create(
            workspace_id=workspace_id, name="PLA", unit=unit_gram,
            min_balance=Decimal("100"),
        )
        MaterialBatch.objects.create(
            material_type=mt,
            qty_initial=Decimal("50"), qty_remaining=Decimal("50"),
            unit_cost=Decimal("1"), purchased_at=date(2025, 1, 1),
        )
        count = tasks.check_material_low.run(str(workspace_id))
        assert count == 1
        alert = Alert.objects.get(workspace_id=workspace_id)
        assert alert.type == Alert.Type.MATERIAL_LOW
        assert "PLA" in alert.title

    def test_no_alert_when_ok(self, workspace_id, unit_gram):
        mt = MaterialType.objects.create(
            workspace_id=workspace_id, name="PLA", unit=unit_gram,
            min_balance=Decimal("100"),
        )
        MaterialBatch.objects.create(
            material_type=mt,
            qty_initial=Decimal("500"), qty_remaining=Decimal("500"),
            unit_cost=Decimal("1"), purchased_at=date(2025, 1, 1),
        )
        count = tasks.check_material_low.run(str(workspace_id))
        assert count == 0
        assert Alert.objects.filter(workspace_id=workspace_id).count() == 0


@pytest.mark.django_db
class TestCheckStockLow:
    def test_creates_alert_when_low(self, workspace_id):
        product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
        variant = ProductVariant.objects.create(product=product, name="Зелёный")
        warehouse = Warehouse.objects.create(
            workspace_id=workspace_id, name="Склад", type=Warehouse.Type.OWN,
        )
        Stock.objects.create(variant=variant, warehouse=warehouse, qty=Decimal("3"))
        count = tasks.check_stock_low.run(str(workspace_id))
        assert count == 1
        assert Alert.objects.get(workspace_id=workspace_id).type == Alert.Type.STOCK_LOW

    def test_no_alert_when_zero(self, workspace_id):
        product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
        variant = ProductVariant.objects.create(product=product, name="Зелёный")
        warehouse = Warehouse.objects.create(
            workspace_id=workspace_id, name="Склад", type=Warehouse.Type.OWN,
        )
        Stock.objects.create(variant=variant, warehouse=warehouse, qty=Decimal("0"))
        count = tasks.check_stock_low.run(str(workspace_id))
        assert count == 0

    def test_no_alert_when_ok(self, workspace_id):
        product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
        variant = ProductVariant.objects.create(product=product, name="Зелёный")
        warehouse = Warehouse.objects.create(
            workspace_id=workspace_id, name="Склад", type=Warehouse.Type.OWN,
        )
        Stock.objects.create(variant=variant, warehouse=warehouse, qty=Decimal("100"))
        count = tasks.check_stock_low.run(str(workspace_id))
        assert count == 0


@pytest.mark.django_db
class TestCheckSyncFailed:
    def test_creates_alert_for_failed(self, workspace_id):
        from apps.integration.models import SyncLog
        SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="wb",
            entity=SyncLog.Entity.ORDERS, status=SyncLog.Status.FAILED,
            error_message="Timeout",
        )
        count = tasks.check_sync_failed.run(str(workspace_id))
        assert count == 1
        alert = Alert.objects.get(workspace_id=workspace_id)
        assert alert.type == Alert.Type.SYNC_FAILED
        assert "Timeout" in alert.message

    def test_no_alert_for_success(self, workspace_id):
        from apps.integration.models import SyncLog
        SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="wb",
            entity=SyncLog.Entity.ORDERS, status=SyncLog.Status.SUCCESS,
        )
        count = tasks.check_sync_failed.run(str(workspace_id))
        assert count == 0