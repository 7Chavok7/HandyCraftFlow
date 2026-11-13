# core/apps/materials/models.py
from decimal import Decimal
from django.db import models

from apps.guide.models import Unit, Color, Country, Manufacturer


class MaterialType(models.Model):
    """Тип материала: PLA черный, ткань хлопок белая, воск лаванда..."""
    
    class Kind(models.TextChoices):
        RAW         = 'raw',        'Сырье'
        CONSUMABLE  = 'consumable', 'Расходник'
        PACKAGING   = 'packaging',  'Упаковка'
        
    workspace_id = models.UUIDField(
        'ID кабинета',
        db_index=True,
    )
    name = models.CharField(
        'Наименование',
        max_length=150,
    )
    kind = models.CharField(
        'Тип',
        max_length=20,
        choices=Kind.choices,
        default=Kind.RAW,
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name='Единица измерения'
    )
    polymer = models.CharField(
        'Полимер/состав',
        max_length=50,
        blank=True,
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Цвет'
    )
    density = models.DecimalField(
        'Плотность, г/см³',
        max_digits=6,
        decimal_places=3,
        blank=True,
        null=True,
    )
    min_balance = models.DecimalField(
        'Минимальный остаток',
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    is_active = models.BooleanField(
        'Активен',
        default=True,
    )
    created_at = models.DateTimeField(
        'Создан',
        auto_now_add=True,
    )
    
    class Meta:
        verbose_name = 'Тип материала'
        verbose_name_plural = 'Типы материалов'
        constraints = [
            models.UniqueConstraint(
            fields =['workspace_id', 'name'],
            name = 'unique_material_type_per_workspace',
            )
        ]
        
    def __str__(self):
        return self.name


class MaterialBatch(models.Model):
    """Партия: конкретная катушка/коробка с ценой."""
    
    material_type = models.ForeignKey(
        MaterialType,
        on_delete=models.PROTECT,
        related_name='batches',
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name='batches',
        null=True,
        blank=True,
    )
    supplier = models.CharField(
        'Где куплено',
        max_length=150,
        blank=True,
    )
    qty_initial = models.DecimalField(
        'Поступило',
        max_digits=12,
        decimal_places=3,
    )
    qty_remaining = models.DecimalField(
        'Осталось',
        max_digits=12,
        decimal_places=3,
    )
    unit_cost = models.DecimalField(
        'Цена за единицу, ₽',
        max_digits=12,
        decimal_places=2,
    )
    purchased_at = models.DateField(
        'Дата покупки',
    )
    is_exhausted = models.BooleanField(
        'Партия закончилась',
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Партия материала"
        verbose_name_plural = "Партии материала"
        ordering = ["purchased_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(qty_remaining__gte=0),
                name="batch_qty_remaining_non_negative",
            ),
        ]
        
    def __str__(self):
        return f"{self.material_type} • {self.manufacturer or '?'} • {self.purchased_at:%d.%m.%Y}"
    
    
class MaterialLedger(models.Model):
    """Журнал движений."""
    
    class MovementType(models.TextChoices):
        INCOME          = 'income',         'Поступление'
        TO_PRODUCTION   = 'to_production',  'В производство'
        WASTE           = 'waste',          'Брак'
        WRITE_OFF       = 'write_off',      'Списание'
        ADJUSTMENT      = 'adjustment',     'Корректировка'
        RETURN          = 'return',         'Возврат'
        
    workspace_id = models.UUIDField(
        "ID кабинета", 
        db_index=True,
    )
    material_type = models.ForeignKey(
        MaterialType, 
        on_delete=models.PROTECT, 
        related_name="ledger_entries",
    )
    batch = models.ForeignKey(
        MaterialBatch, 
        on_delete=models.PROTECT, 
        related_name="ledger_entries",
        null=True, 
        blank=True,
    )
    movement_type = models.CharField(
        "Тип движения", 
        max_length=20, 
        choices=MovementType.choices,
    )
    qty = models.DecimalField(
        "Количество (со знаком)", 
        max_digits=12, 
        decimal_places=3,
    )
    unit_cost_snapshot = models.DecimalField(
        "Цена на момент движения, ₽", 
        max_digits=12, 
        decimal_places=4,
        null=True, 
        blank=True,
    )
    comment = models.TextField(
        "Комментарий", 
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Движение материала"
        verbose_name_plural = "Движения материалов"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["material_type", "-created_at"]),
            models.Index(fields=["workspace_id", "-created_at"]),
        ]

    def __str__(self):
        sign = "+" if self.qty >= 0 else ""
        return f"{self.material_type} | {sign}{self.qty} ({self.get_movement_type_display()})"