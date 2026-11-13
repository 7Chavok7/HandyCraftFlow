# core/apps/alerts/services.py
from apps.alerts.models import Alert


def create_alert(
    *, workspace_id, type, title, message="", severity=None,
    related_object_id=None,
) -> Alert:
    """Создать уведомление. Если severity не задан — по типу."""
    if severity is None:
        severity = _default_severity(type)

    return Alert.objects.create(
        workspace_id=workspace_id,
        type=type,
        severity=severity,
        title=title,
        message=message,
        related_object_id=related_object_id,
    )


def _default_severity(alert_type: str) -> str:
    mapping = {
        Alert.Type.MATERIAL_LOW: Alert.Severity.WARNING,
        Alert.Type.STOCK_LOW: Alert.Severity.WARNING,
        Alert.Type.PROMOTION_INCOMING: Alert.Severity.INFO,
        Alert.Type.MARGIN_BELOW_TARGET: Alert.Severity.CRITICAL,
        Alert.Type.SYNC_FAILED: Alert.Severity.CRITICAL,
        Alert.Type.RESERVATION_CONFLICT: Alert.Severity.CRITICAL,
    }
    return mapping.get(alert_type, Alert.Severity.INFO)