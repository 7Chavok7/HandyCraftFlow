# core/apps/integration/tasks.py
from celery import shared_task
from django.utils import timezone

from .models import SyncLog


@shared_task
def sync_entity(workspace_id: str, marketplace: str, entity: str):
    """Заглушка синхронизации: пишет SyncLog с успехом, без реального API."""
    log = SyncLog.objects.create(
        workspace_id=workspace_id,
        marketplace=marketplace,
        entity=entity,
        status=SyncLog.Status.RUNNING,
        started_at=timezone.now(),
    )

    try:
        # здесь позже будет реальный вызов клиента
        items_processed = 0

        log.status = SyncLog.Status.SUCCESS
        log.items_processed = items_processed
        log.finished_at = timezone.now()
        log.save(update_fields=[
            "status", "items_processed", "finished_at",
        ])
        return log.pk
    except Exception as exc:
        log.status = SyncLog.Status.FAILED
        log.error_message = str(exc)
        log.finished_at = timezone.now()
        log.save(update_fields=["status", "error_message", "finished_at"])
        raise


@shared_task
def sync_orders(workspace_id: str, marketplace: str):
    return sync_entity(workspace_id, marketplace, SyncLog.Entity.ORDERS)


@shared_task
def sync_stocks(workspace_id: str, marketplace: str):
    return sync_entity(workspace_id, marketplace, SyncLog.Entity.STOCKS)


@shared_task
def sync_prices(workspace_id: str, marketplace: str):
    return sync_entity(workspace_id, marketplace, SyncLog.Entity.PRICES)


@shared_task
def sync_promotions(workspace_id: str, marketplace: str):
    return sync_entity(workspace_id, marketplace, SyncLog.Entity.PROMOTIONS)


@shared_task
def sync_finances(workspace_id: str, marketplace: str):
    return sync_entity(workspace_id, marketplace, SyncLog.Entity.FINANCES)