# farm/apps/printers/services.py
from decimal import Decimal

from django.utils import timezone

from .models import FarmJob


def assign_job(*, farm_job: FarmJob, printer, ams_slot=None) -> FarmJob:
    """Назначить задание на принтер (смена принтера)."""
    farm_job.printer = printer
    farm_job.ams_slot = ams_slot
    farm_job.status = FarmJob.Status.ASSIGNED
    farm_job.save(update_fields=["printer", "ams_slot", "status"])
    return farm_job


def start_job(*, farm_job: FarmJob) -> FarmJob:
    """Начать печать."""
    if farm_job.status not in (
        FarmJob.Status.ASSIGNED, FarmJob.Status.PAUSED,
    ):
        raise ValueError(f"Нельзя начать из статуса {farm_job.status}")
    farm_job.status = FarmJob.Status.PRINTING
    farm_job.started_at = farm_job.started_at or timezone.now()
    farm_job.save(update_fields=["status", "started_at"])
    return farm_job


def pause_job(*, farm_job: FarmJob) -> FarmJob:
    """Пауза."""
    if farm_job.status != FarmJob.Status.PRINTING:
        raise ValueError("На паузу можно поставить только печатающее задание")
    farm_job.status = FarmJob.Status.PAUSED
    farm_job.save(update_fields=["status"])
    return farm_job


def cancel_job(*, farm_job: FarmJob, comment: str = "") -> FarmJob:
    """Отмена."""
    if farm_job.status in (FarmJob.Status.DONE, FarmJob.Status.CANCELLED):
        raise ValueError("Задание уже завершено или отменено")
    farm_job.status = FarmJob.Status.CANCELLED
    farm_job.finished_at = timezone.now()
    if comment:
        farm_job.comment = (farm_job.comment + "\n" + comment).strip()
    farm_job.save(update_fields=["status", "finished_at", "comment"])
    return farm_job


def finish_job(
    *,
    farm_job: FarmJob,
    qty_done: int,
    qty_waste: int = 0,
    actual_weight: Decimal | None = None,
    actual_time_min: int | None = None,
    comment: str = "",
) -> FarmJob:
    """Завершить печать и отправить отчёт в Core (через client-заглушку)."""
    if farm_job.status not in (
        FarmJob.Status.PRINTING, FarmJob.Status.PAUSED,
    ):
        raise ValueError(f"Нельзя завершить из статуса {farm_job.status}")

    farm_job.qty_done = qty_done
    farm_job.qty_waste = qty_waste
    farm_job.actual_weight = actual_weight
    farm_job.actual_time_min = actual_time_min
    farm_job.status = FarmJob.Status.DONE
    farm_job.finished_at = timezone.now()
    if comment:
        farm_job.comment = (farm_job.comment + "\n" + comment).strip()
    farm_job.save(update_fields=[
        "qty_done", "qty_waste", "actual_weight", "actual_time_min",
        "status", "finished_at", "comment",
    ])

    # отправка в Core — через клиент-заглушку
    from .core_client import send_report_to_core
    send_report_to_core(
        production_job_id=str(farm_job.production_job_id),
        qty_done=qty_done,
        qty_waste=qty_waste,
        actual_weight=actual_weight,
        actual_time_min=actual_time_min,
        comment=comment,
    )

    return farm_job