# core/apps/promo/models.py
from django.db import models

from apps.catalog.models import ProductVariant


class Promotion(models.Model):
    """Акция площадки (WB, Ozon, Я.Маркет)."""

    class Marketplace(models.TextChoices):
        WB = "wb", "Wildberries"
        OZON = "ozon", "Ozon"
        YANDEX = "yandex", "Яндекс Маркет"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    marketplace = models.CharField(
        "Площадка", max_length=20, choices=Marketplace.choices,
    )
    external_id = models.CharField(
        "ID акции на площадке", max_length=100, blank=True,
    )
    name = models.CharField("Название", max_length=200)
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Конец")
    discount_percent = models.DecimalField(
        "Скидка, %", max_digits=5, decimal_places=2, default=0,
    )
    raw_payload = models.JSONField(
        "Сырые данные с площадки", default=dict, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ["-starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace_id", "marketplace", "external_id"],
                name="unique_promotion_per_workspace_marketplace_external",
                condition=models.Q(external_id__gt=""),
            ),
        ]
        indexes = [
            models.Index(fields=["workspace_id", "marketplace", "-starts_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_marketplace_display()})"


class PromotionItem(models.Model):
    """Попадание варианта в акцию с прогнозом маржи и решением."""

    class Decision(models.TextChoices):
        PENDING = "pending", "Не решено"
        ACCEPTED = "accepted", "Участвуем"
        DECLINED = "declined", "Отказались"

    promotion = models.ForeignKey(
        Promotion, on_delete=models.CASCADE, related_name="items",
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="promotion_items",
    )
    proposed_price = models.DecimalField(
        "Предложенная цена, ₽", max_digits=12, decimal_places=2,
    )
    margin_at_proposed = models.DecimalField(
        "Маржа на момент решения, ₽", max_digits=12, decimal_places=2,
        null=True, blank=True,
    )
    snapshot_cost = models.DecimalField(
        "Себестоимость на момент решения, ₽", max_digits=12, decimal_places=2,
        null=True, blank=True,
    )
    decision = models.CharField(
        "Решение", max_length=20,
        choices=Decision.choices, default=Decision.PENDING,
    )
    decided_at = models.DateTimeField("Когда решено", null=True, blank=True)
    comment = models.CharField("Комментарий", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар в акции"
        verbose_name_plural = "Товары в акциях"
        ordering = ["promotion", "variant"]
        constraints = [
            models.UniqueConstraint(
                fields=["promotion", "variant"],
                name="unique_variant_per_promotion",
            ),
        ]

    def __str__(self):
        return f"{self.promotion} / {self.variant} → {self.get_decision_display()}"