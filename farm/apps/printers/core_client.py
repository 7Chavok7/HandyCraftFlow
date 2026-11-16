# farm/apps/printers/core_client.py
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_report_to_core(
    *,
    production_job_id: str,
    qty_done: int,
    qty_waste: int = 0,
    actual_weight=None,
    actual_time_min: int | None = None,
    comment: str = "",
    timeout: int = 10,
) -> bool:
    """Отправить отчёт в Core: POST /api/v1/jobs/{id}/report/.

    Заголовок X-Internal-Token — общий секрет (settings.INTERNAL_API_TOKEN).
    Возвращает True при 2xx, иначе логирует и возвращает False.
    """
    url = f"{settings.CORE_API_URL.rstrip('/')}/api/v1/jobs/{production_job_id}/report/"
    payload = {
        "qty_done": qty_done,
        "qty_waste": qty_waste,
        "comment": comment,
    }
    if actual_weight is not None:
        payload["actual_weight"] = str(actual_weight)
    if actual_time_min is not None:
        payload["actual_time_min"] = actual_time_min

    headers = {
        "X-Internal-Token": getattr(settings, "INTERNAL_API_TOKEN", ""),
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=timeout,
        )
        if 200 <= response.status_code < 300:
            logger.info(
                "[CORE] report ok production_job=%s status=%s",
                production_job_id, response.status_code,
            )
            return True
        logger.warning(
            "[CORE] report failed production_job=%s status=%s body=%s",
            production_job_id, response.status_code, response.text[:500],
        )
        return False
    except requests.RequestException as exc:
        logger.error(
            "[CORE] report exception production_job=%s: %s",
            production_job_id, exc,
        )
        return False