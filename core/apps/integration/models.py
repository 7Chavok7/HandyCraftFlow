# core/apps/integration/models.py
from django.db import models


class SyncLog(models.Model):
    """Журнал синхронизаций с площадками. Заглушка — без реальных вызовов."""

    class Entity(models.TextChoices):
        ORDERS = "orders", "Заказы"
        STOCKS = "stocks", "Остатки"
        PRICES = "prices", "Цены"
        PROMOTIONS = "promotions", "Акции"
        FINANCES = "finances", "Финансы"

    class Status(models.TextChoices):
        PENDING = "pending", "В очереди"
        RUNNING = "running", "Выполняется"
        SUCCESS = "success", "Успех"
        FAILED = "failed", "Ошибка"
        SKIPPED = "skipped", "Пропущено"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    marketplace = models.CharField("Площадка", max_length=20)
    entity = models.CharField("Сущность", max_length=20, choices=Entity.choices)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.PENDING,
    )
    items_processed = models.PositiveIntegerField("Обработано", default=0)
    items_failed = models.PositiveIntegerField("Ошибок", default=0)
    error_message = models.TextField("Сообщение об ошибке", blank=True)
    started_at = models.DateTimeField("Начало", null=True, blank=True)
    finished_at = models.DateTimeField("Конец", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Синхронизация"
        verbose_name_plural = "Синхронизации"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace_id", "marketplace", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.marketplace} / {self.get_entity_display()} → {self.get_status_display()}"