# core/apps/alerts/tasks.py
from celery import shared_task
from django.db.models import F, Sum

from apps.alerts.models import Alert
from apps.alerts.services import create_alert
from apps.materials.models import MaterialType
from apps.warehouse.models import Stock


@shared_task
def check_material_low(workspace_id: str):
    """Проверить материалы: остаток < min_balance."""
    material_types = MaterialType.objects.filter(
        workspace_id=workspace_id, is_active=True, min_balance__gt=0,
    )
    created = 0
    for mt in material_types:
        agg = mt.batches.filter(is_exhausted=False).aggregate(
            total=Sum("qty_remaining"),
        )
        balance = agg["total"] or 0
        if balance < mt.min_balance:
            create_alert(
                workspace_id=workspace_id,
                type=Alert.Type.MATERIAL_LOW,
                title=f"Мало материала: {mt.name}",
                message=f"Остаток {balance} {mt.unit}, минимум {mt.min_balance}",
                related_object_id=mt.id,
            )
            created += 1
    return created


@shared_task
def check_stock_low(workspace_id: str):
    """Проверить остатки готовых изделий: qty < минимального порога.

    Порог берём из Recipe (пока нет — считаем 5 шт по умолчанию).
    """
    stocks = Stock.objects.filter(
        warehouse__workspace_id=workspace_id,
        warehouse__is_active=True,
    ).select_related("variant", "warehouse")
    created = 0
    for stock in stocks:
        threshold = 5  # MVP: фиксированный порог
        if stock.qty < threshold and stock.qty > 0:
            create_alert(
                workspace_id=workspace_id,
                type=Alert.Type.STOCK_LOW,
                title=f"Мало товара: {stock.variant}",
                message=f"Остаток {stock.qty} @ {stock.warehouse}",
                related_object_id=stock.variant_id,
            )
            created += 1
    return created


@shared_task
def check_sync_failed(workspace_id: str):
    """Проверить неудачные синхронизации за последние 24 часа."""
    from django.utils import timezone
    from datetime import timedelta
    from apps.integration.models import SyncLog

    since = timezone.now() - timedelta(hours=24)
    failed = SyncLog.objects.filter(
        workspace_id=workspace_id,
        status=SyncLog.Status.FAILED,
        created_at__gte=since,
    )
    created = 0
    for log in failed:
        create_alert(
            workspace_id=workspace_id,
            type=Alert.Type.SYNC_FAILED,
            title=f"Ошибка синхронизации: {log.marketplace} / {log.get_entity_display()}",
            message=log.error_message or "Без деталей",
            related_object_id=log.id,
        )
        created += 1
    return created