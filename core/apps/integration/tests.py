import uuid

import pytest
from django.utils import timezone

from apps.integration.models import SyncLog
from apps.integration.clients import OzonClient, WBClient
from apps.integration import tasks


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


# --- SyncLog ---

@pytest.mark.django_db
class TestSyncLog:
    def test_str(self, workspace_id):
        log = SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="wb",
            entity=SyncLog.Entity.ORDERS,
        )
        assert "wb" in str(log)
        assert "Заказы" in str(log)
        assert "В очереди" in str(log)

    def test_default_status_pending(self, workspace_id):
        log = SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="ozon",
            entity=SyncLog.Entity.STOCKS,
        )
        assert log.status == SyncLog.Status.PENDING

    def test_defaults_zero(self, workspace_id):
        log = SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="wb",
            entity=SyncLog.Entity.PRICES,
        )
        assert log.items_processed == 0
        assert log.items_failed == 0

    def test_error_message_blank(self, workspace_id):
        log = SyncLog.objects.create(
            workspace_id=workspace_id, marketplace="wb",
            entity=SyncLog.Entity.ORDERS,
        )
        assert log.error_message == ""


# --- Clients (заглушки) ---

class TestOzonClient:
    def test_returns_empty_lists(self):
        c = OzonClient(client_id="123", api_key="secret")
        assert c.fetch_orders() == []
        assert c.fetch_stocks() == []
        assert c.fetch_prices() == []
        assert c.fetch_promotions() == []
        assert c.fetch_finances() == []


class TestWBClient:
    def test_returns_empty_lists(self):
        c = WBClient(token="token")
        assert c.fetch_orders() == []
        assert c.fetch_stocks() == []
        assert c.fetch_prices() == []
        assert c.fetch_promotions() == []
        assert c.fetch_finances() == []


# --- Tasks ---

@pytest.mark.django_db
class TestTasks:
    def test_sync_entity_success(self, workspace_id):
        task_result = tasks.sync_entity.run(
            str(workspace_id), "wb", SyncLog.Entity.ORDERS,
        )
        log = SyncLog.objects.get(pk=task_result)
        assert log.status == SyncLog.Status.SUCCESS
        assert log.items_processed == 0
        assert log.started_at is not None
        assert log.finished_at is not None

    def test_sync_orders_creates_success_log(self, workspace_id):
        task_result = tasks.sync_orders.run(str(workspace_id), "wb")
        log = SyncLog.objects.get(pk=task_result)
        assert log.entity == SyncLog.Entity.ORDERS
        assert log.status == SyncLog.Status.SUCCESS

    def test_sync_stocks_creates_log(self, workspace_id):
        task_result = tasks.sync_stocks.run(str(workspace_id), "ozon")
        log = SyncLog.objects.get(pk=task_result)
        assert log.entity == SyncLog.Entity.STOCKS
        assert log.marketplace == "ozon"

    def test_sync_prices_creates_log(self, workspace_id):
        task_result = tasks.sync_prices.run(str(workspace_id), "wb")
        log = SyncLog.objects.get(pk=task_result)
        assert log.entity == SyncLog.Entity.PRICES

    def test_sync_promotions_creates_log(self, workspace_id):
        task_result = tasks.sync_promotions.run(str(workspace_id), "ozon")
        log = SyncLog.objects.get(pk=task_result)
        assert log.entity == SyncLog.Entity.PROMOTIONS

    def test_sync_finances_creates_log(self, workspace_id):
        task_result = tasks.sync_finances.run(str(workspace_id), "wb")
        log = SyncLog.objects.get(pk=task_result)
        assert log.entity == SyncLog.Entity.FINANCES