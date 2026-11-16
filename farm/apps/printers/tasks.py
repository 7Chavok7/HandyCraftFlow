# farm/apps/printers/tasks.py
import logging
import uuid as uuid_module

from pathlib import Path
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ValidationError

from .gcode_parser import parse_gcode_header
from .models import FarmJob

logger = logging.getLogger(__name__)


@shared_task
def watch_gcode_folder() -> dict:
    """Сканирует папку GCODE_WATCH_DIR, парсит новые gcode и обновляет FarmJob.

    Логика сопоставления: по имени файла без расширения ищем FarmJob.comment
    или production_job_id (если имя файла — это UUID production_job_id).
    В MVP: если имя файла содержит UUID — ищем по production_job_id.
    Иначе — пропускаем (не смогли сопоставить).

    Возвращает {"scanned": N, "matched": M}.
    """
    watch_dir = getattr(settings, "GCODE_WATCH_DIR", "")
    if not watch_dir:
        logger.debug("GCODE_WATCH_DIR не задан — watcher пропущен")
        return {"scanned": 0, "matched": 0}

    path = Path(watch_dir)
    if not path.exists() or not path.is_dir():
        logger.warning("GCODE_WATCH_DIR не существует: %s", watch_dir)
        return {"scanned": 0, "matched": 0}

    scanned = 0
    matched = 0

    for gcode_file in path.glob("*.gcode"):
        scanned += 1
        stem = gcode_file.stem  # имя без .gcode

        # пробуем найти FarmJob по production_job_id (имя файла = UUID)
        try:
            prod_uuid = uuid_module.UUID(stem)
        except (ValueError, AttributeError):
            continue

        try:
            farm_job = FarmJob.objects.get(production_job_id=prod_uuid)
        except FarmJob.DoesNotExist:
            continue

        if farm_job.actual_weight is not None and farm_job.actual_time_min is not None:
            # уже заполнено — пропускаем
            continue

        parsed = parse_gcode_header(gcode_file)
        if parsed["weight_g"] is not None:
            farm_job.actual_weight = parsed["weight_g"]
        if parsed["time_min"] is not None:
            farm_job.actual_time_min = parsed["time_min"]
        farm_job.save(update_fields=["actual_weight", "actual_time_min"])
        matched += 1
        logger.info(
            "gcode %s → FarmJob #%s: weight=%s time=%s",
            gcode_file.name, farm_job.pk,
            parsed["weight_g"], parsed["time_min"],
        )

    return {"scanned": scanned, "matched": matched}