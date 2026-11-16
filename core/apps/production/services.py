# core/apps/production/services.py
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.materials.models import MaterialLedger
from apps.production.models import ProductionJob
from apps.warehouse.models import Stock, StockLedger


@transaction.atomic
def complete_production_job(
    *,
    job: ProductionJob,
    qty_done: int,
    qty_waste: int = 0,
    actual_weight: Decimal | None = None,
    actual_time_min: int | None = None,
    comment: str = "",
) -> ProductionJob:
    """Завершить ProductionJob: списать материал, принять изделия на склад.

    Вызывается из Farm (через report) или вручную (если Farm недоступен).
    """
    if job.status == ProductionJob.Status.DONE:
        raise ValueError("Задание уже завершено")

    if qty_done < 0 or qty_waste < 0:
        raise ValueError("Количество не может быть отрицательным")

    # 1. Списать материал с партии (если указана)
    if job.material_batch and actual_weight:
        _write_off_material(
            job=job, weight=actual_weight, comment=comment,
        )

    # 2. Принять готовые изделия на свой склад
    if qty_done > 0:
        _receive_finished_goods(job=job, qty_done=qty_done, comment=comment)

    # 3. Обновить задание
    job.qty_done = qty_done
    job.qty_waste = qty_waste
    job.actual_weight = actual_weight
    job.actual_time_min = actual_time_min
    job.status = ProductionJob.Status.DONE
    job.finished_at = timezone.now()
    if comment:
        job.comment = (job.comment + "\n" + comment).strip()
    job.save(update_fields=[
        "qty_done", "qty_waste", "actual_weight", "actual_time_min",
        "status", "finished_at", "comment",
    ])

    return job


def _write_off_material(*, job: ProductionJob, weight: Decimal, comment: str):
    """Списать материал с партии. weight — в единицах учёта материала."""
    batch = job.material_batch
    if weight <= 0:
        return
    if batch.qty_remaining < weight:
        raise ValueError(
            f"Недостаточно материала в партии: осталось {batch.qty_remaining}, "
            f"требуется {weight}"
        )

    MaterialLedger.objects.create(
        workspace_id=job.workspace_id,
        material_type=batch.material_type,
        batch=batch,
        movement_type=MaterialLedger.MovementType.TO_PRODUCTION,
        qty=-weight,
        unit_cost_snapshot=batch.unit_cost,
        comment=comment or f"Списание по заданию #{job.pk}",
    )

    batch.qty_remaining -= weight
    if batch.qty_remaining <= 0:
        batch.qty_remaining = Decimal("0")
        batch.is_exhausted = True
    batch.save(update_fields=["qty_remaining", "is_exhausted"])


def _receive_finished_goods(*, job: ProductionJob, qty_done: int, comment: str):
    """Принять готовые изделия на свой склад workspace."""
    from apps.warehouse.models import Warehouse

    own_warehouse = Warehouse.objects.filter(
        workspace_id=job.workspace_id, type=Warehouse.Type.OWN,
    ).first()
    if not own_warehouse:
        raise ValueError(
            f"У workspace {job.workspace_id} нет своего склада (type=own). "
            f"Создайте склад перед завершением задания."
        )

    stock, _ = Stock.objects.get_or_create(
        variant=job.variant,
        warehouse=own_warehouse,
        defaults={"qty": Decimal("0"), "reserved_qty": Decimal("0")},
    )
    stock.qty += Decimal(qty_done)
    stock.save(update_fields=["qty", "updated_at"])

    StockLedger.objects.create(
        variant=job.variant,
        warehouse=own_warehouse,
        movement_type=StockLedger.MovementType.PRODUCTION_IN,
        qty=Decimal(qty_done),
        comment=comment or f"Поступление по заданию #{job.pk}",
    )