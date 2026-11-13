# core/apps/pricing/models.py
from django.db import models

from apps.catalog.models import ProductVariant


class PriceRule(models.Model):
    """Правило ценообразования для варианта. Одна запись = одна красная линия."""

    class Strategy(models.TextChoices):
        FIXED = "fixed", "Фиксированная цена"
        MIN_PRICE_GUARD = "min_price_guard", "Только защита от убытка"
        MARGIN_GUARD = "margin_guard", "Защита по целевой марже"

    variant = models.OneToOneField(
        ProductVariant, on_delete=models.CASCADE, related_name="price_rule",
    )
    strategy = models.CharField(
        "Стратегия", max_length=20,
        choices=Strategy.choices, default=Strategy.MIN_PRICE_GUARD,
    )
    min_margin_percent = models.DecimalField(
        "Минимальная маржа, %", max_digits=5, decimal_places=2, default=0,
    )
    target_margin_percent = models.DecimalField(
        "Целевая маржа, %", max_digits=5, decimal_places=2, default=30,
    )
    fixed_price = models.DecimalField(
        "Фиксированная цена, ₽", max_digits=12, decimal_places=2,
        null=True, blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Правило цены"
        verbose_name_plural = "Правила цен"

    def __str__(self):
        return f"{self.variant}: min {self.min_margin_percent}% / target {self.target_margin_percent}%"


class PriceHistory(models.Model):
    """Снимок цены при изменении. Нужен для аудита и отчётов."""

    class Source(models.TextChoices):
        MANUAL = "manual", "Вручную"
        PROMOTION = "promotion", "Акция МП"
        REPRICING = "repricing", "Автокоррекция"
        SYNC = "sync", "Синхронизация с МП"

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="price_history",
    )
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2)
    source = models.CharField(
        "Источник изменения", max_length=20,
        choices=Source.choices, default=Source.MANUAL,
    )
    comment = models.CharField("Комментарий", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "История цены"
        verbose_name_plural = "История цен"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["variant", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.variant} → {self.price} ₽ ({self.get_source_display()})"
    
    
class MarketplaceFee(models.Model):
    """Комиссия и логистика площадки по категории."""

    marketplace = models.CharField(
        "Площадка", max_length=20,
        choices=[
            ("wb", "Wildberries"),
            ("ozon", "Ozon"),
            ("yandex", "Яндекс Маркет"),
            ("own", "Свой сайт"),
            ("offline", "Офлайн"),
        ],
    )
    category = models.ForeignKey(
        "catalog.Category", on_delete=models.PROTECT,
        null=True, blank=True, related_name="marketplace_fees",
        verbose_name="Категория (если null — общая ставка)",
    )
    commission_percent = models.DecimalField(
        "Комиссия, %", max_digits=5, decimal_places=2, default=0,
    )
    logistics_cost = models.DecimalField(
        "Логистика, ₽", max_digits=12, decimal_places=2, default=0,
    )
    valid_from = models.DateField("Действует с", null=True, blank=True)
    valid_to = models.DateField("Действует до", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комиссия площадки"
        verbose_name_plural = "Комиссии площадок"
        ordering = ["marketplace", "category"]
        constraints = [
            models.UniqueConstraint(
                fields=["marketplace", "category"],
                name="unique_fee_per_marketplace_category",
                nulls_distinct=False,
            ),
        ]

    def __str__(self):
        cat = self.category.name if self.category else "общая"
        return f"{self.get_marketplace_display()} / {cat}: {self.commission_percent}% + {self.logistics_cost} ₽"