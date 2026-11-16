# farm/apps/printers/core_client.py
"""
Заглушка клиента Core. Пока не делает HTTP — только логирует.
При деплое заменим на реальный requests.post(CORE_API_URL + ...).
"""
import logging

logger = logging.getLogger(__name__)


def send_report_to_core(
    *,
    production_job_id: str,
    qty_done: int,
    qty_waste: int = 0,
    actual_weight=None,
    actual_time_min: int | None = None,
    comment: str = "",
) -> bool:
    logger.info(
        "[CORE-STUB] report production_job=%s qty_done=%s waste=%s weight=%s time=%s",
        production_job_id, qty_done, qty_waste, actual_weight, actual_time_min,
    )
    return True