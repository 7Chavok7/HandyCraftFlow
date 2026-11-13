# core/apps/alerts/models.py
from django.db import models


class Alert(models.Model):
    """Уведомление пользователю."""

    class Type(models.TextChoices):
        MATERIAL_LOW = "material_low", "Мало материала"
        STOCK_LOW = "stock_low", "Мало готового товара"
        PROMOTION_INCOMING = "promotion_incoming", "Товар попал в акцию"
        MARGIN_BELOW_TARGET = "margin_below_target", "Маржа ниже целевой"
        SYNC_FAILED = "sync_failed", "Ошибка синхронизации"
        RESERVATION_CONFLICT = "reservation_conflict", "Конфликт резерва"

    class Severity(models.TextChoices):
        INFO = "info", "Информация"
        WARNING = "warning", "Внимание"
        CRITICAL = "critical", "Критично"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    type = models.CharField("Тип", max_length=30, choices=Type.choices)
    severity = models.CharField(
        "Важность", max_length=20, choices=Severity.choices,
        default=Severity.INFO,
    )
    title = models.CharField("Заголовок", max_length=200)
    message = models.TextField("Сообщение", blank=True)
    related_object_id = models.UUIDField(
        "ID связанного объекта", null=True, blank=True,
    )
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace_id", "-created_at"]),
            models.Index(fields=["workspace_id", "is_read"]),
        ]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"