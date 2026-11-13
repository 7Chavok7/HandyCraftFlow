# core/apps/warehouse/models.py
from django.db import models

from apps.catalog.models import ProductVariant


class SellerAccount(models.Model):
    """Кабинет на маркетплейсе. Заглушка под интеграции."""

    class Marketplace(models.TextChoices):
        WB = "wb", "Wildberries"
        OZON = "ozon", "Ozon"
        YANDEX = "yandex", "Яндекс Маркет"
        OWN = "own", "Свой сайт"
        OFFLINE = "offline", "Офлайн"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    marketplace = models.CharField(
        "Площадка", max_length=20, choices=Marketplace.choices,
    )
    name = models.CharField("Название кабинета", max_length=150, blank=True)
    client_id = models.CharField("Client ID (Ozon)", max_length=100, blank=True)
    encrypted_token = models.TextField("Токен (шифрованный)", blank=True)
    is_active = models.BooleanField("Активен", default=True)
    last_sync_at = models.DateTimeField("Последняя синхронизация", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кабинет МП"
        verbose_name_plural = "Кабинеты МП"
        constraints = [
            models.UniqueConstraint(
                fields=["workspace_id", "marketplace", "name"],
                name="unique_account_per_workspace_marketplace_name",
            ),
        ]

    def __str__(self):
        return f"{self.get_marketplace_display()} · {self.name or self.pk}"


class Warehouse(models.Model):
    """Склад: свой, FBO/FBS маркетплейса, офлайн."""

    class Type(models.TextChoices):
        OWN = "own", "Свой склад"
        FBO = "fbo", "FBO маркетплейса"
        FBS = "fbs", "FBS маркетплейса"
        OFFLINE = "offline", "Офлайн-точка"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    name = models.CharField("Название", max_length=150)
    type = models.CharField("Тип", max_length=20, choices=Type.choices)
    seller_account = models.ForeignKey(
        SellerAccount, on_delete=models.PROTECT,
        null=True, blank=True, related_name="warehouses",
        verbose_name="Кабинет МП",
    )
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        constraints = [
            models.UniqueConstraint(
                fields=["workspace_id", "name"],
                name="unique_warehouse_per_workspace",
            ),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Stock(models.Model):
    """Кэш остатков по варианту и складу."""

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="stocks",
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stocks",
    )
    qty = models.DecimalField("Количество", max_digits=12, decimal_places=3, default=0)
    reserved_qty = models.DecimalField(
        "Зарезервировано", max_digits=12, decimal_places=3, default=0,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "warehouse"],
                name="unique_stock_per_variant_warehouse",
            ),
        ]

    def __str__(self):
        return f"{self.variant} @ {self.warehouse}: {self.qty}"

    @property
    def available_qty(self):
        """Доступно к продаже = остаток − резерв."""
        return self.qty - self.reserved_qty


class StockLedger(models.Model):
    """Журнал движений остатков. Истина — здесь."""

    class MovementType(models.TextChoices):
        PRODUCTION_IN = "production_in", "Поступление из производства"
        SALE = "sale", "Продажа"
        RETURN = "return", "Возврат"
        WRITE_OFF = "write_off", "Списание"
        ADJUSTMENT = "adjustment", "Корректировка"
        TRANSFER = "transfer", "Перемещение"
        SYNC = "sync", "Синхронизация с МП"
        RESERVE = "reserve", "Резерв"
        UNRESERVE = "unreserve", "Снятие резерва"

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="stock_ledger_entries",
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="stock_ledger_entries",
    )
    movement_type = models.CharField(
        "Тип движения", max_length=20, choices=MovementType.choices,
    )
    qty = models.DecimalField("Количество (со знаком)", max_digits=12, decimal_places=3)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Движение остатка"
        verbose_name_plural = "Движения остатков"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["variant", "-created_at"]),
            models.Index(fields=["warehouse", "-created_at"]),
        ]

    def __str__(self):
        sign = "+" if self.qty >= 0 else ""
        return (
            f"{self.variant} @ {self.warehouse} | {sign}{self.qty} "
            f"({self.get_movement_type_display()})"
        )