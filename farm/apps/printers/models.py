# farm/apps/printers/models.py
from django.db import models


class Printer(models.Model):
    """3D-принтер фермы. Farm не знает про Core — только equipment_id."""

    class Status(models.TextChoices):
        FREE = "free", "Свободен"
        PRINTING = "printing", "Печатает"
        PAUSED = "paused", "Пауза"
        ERROR = "error", "Ошибка"
        OFFLINE = "offline", "Не в сети"

    workspace_id = models.UUIDField("ID кабинета (из Core)", db_index=True)
    name = models.CharField("Имя", max_length=100)
    model = models.CharField("Модель", max_length=50, blank=True)  # A1 mini, P1S, X1C
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    serial = models.CharField("Серийный номер", max_length=100, blank=True)
    ams_slots_count = models.PositiveSmallIntegerField("Слотов AMS", default=0)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.OFFLINE,
    )
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Принтер"
        verbose_name_plural = "Принтеры"
        constraints = [
            models.UniqueConstraint(
                fields=["workspace_id", "name"],
                name="unique_printer_per_workspace",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.model or 'unknown'})"


class AmsSlot(models.Model):
    """Слот AMS. material_batch_id — ссылка на партию из Core (без FK)."""

    printer = models.ForeignKey(
        Printer, on_delete=models.CASCADE, related_name="ams_slots",
    )
    slot_number = models.PositiveSmallIntegerField("Номер слота")  # 1..4
    material_batch_id = models.UUIDField(
        "ID партии (из Core)", null=True, blank=True,
    )

    class Meta:
        verbose_name = "Слот AMS"
        verbose_name_plural = "Слоты AMS"
        constraints = [
            models.UniqueConstraint(
                fields=["printer", "slot_number"],
                name="unique_slot_per_printer",
            )
        ]

    def __str__(self):
        return f"{self.printer.name} · слот {self.slot_number}"