# core/apps/workspace/models.py
import uuid
from django.conf import settings
from django.db import models


class Workspace(models.Model):
    """Рабочий кабинет - изолирует все данные пользователя"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        "Название",
        max_length=100
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='workspaces',
        verbose_name='Владлец'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Рабочий кабинет'
        verbose_name_plural = 'Рабочие кабинеты'
        
    def __str__(self):
        return f"{self.name}"
    
    
class WorkspaceSettings(models.Model):
    """"Экономические настройки кабинета"""
    
    class LaborMode(models.TextChoices):
        MANUAL_RATE = 'manual_rate', 'Мое время стоит XX ₽/час.'
        INCOME_GOAL = 'income_goal', 'Хочу зарабатывать XXX ₽/мес.'
        IGNORE_LABOR = 'ignore_labor', 'Не учитывать мой труд'
    
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name='Кабинет',
    )
    labor_mode = models.CharField(
        "Режим расчета труда",
        max_length=20,
        choices=LaborMode.choices,
        default=LaborMode.IGNORE_LABOR,
    )
    labor_rate = models.DecimalField(
        "Ставка часа, ₽",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    income_goal = models.DecimalField(
        "Цель дохода в месяц, ₽",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    work_hours_per_day = models.DecimalField(
        "Часов работы в день",
        max_digits=4,
        decimal_places=1,
        default=4,
    )
    target_margin_percent = models.DecimalField(
        "Целевая маржа, %",
        max_digits=5,
        decimal_places=2,
        default=35,
    )
    electricity_rate = models.DecimalField(
        "Тариф электроэнергии, ₽/кВт•ч.",
        max_digits=6,
        decimal_places=2,
        default=7,
    )
    tax_rate = models.DecimalField(
        "Налогооблажение",
        max_digits=5,
        decimal_places=2,
        default=4,
    )
    equipment_hour_cost = models.DecimalField(
        "Стоимость часа оборудования, ₽", 
        max_digits=12, 
        decimal_places=2, 
        default=0,
    )
    
    class Meta:
        verbose_name = 'Настройки кабинета'
        verbose_name_plural = 'Настройки кабинетов'
        
    def __str__(self):
        return f"Настройки: {self.workspace}"
    
    @property
    def effective_labor_rate(self):
        """Ставка часа с учетом режима труда
        
        - manual_rate → labor_rate
        - income_goal → income_goal / (work_hours_per_day * 22)
        - ignore_labor → 0
        """
        from decimal import Decimal
        
        if self.labor_mode == self.LaborMode.IGNORE_LABOR:
            return Decimal('0')
        if self.labor_mode == self.LaborMode.MANUAL_RATE:
            return self.labor_rate or Decimal('0')
        if self.labor_mode == self.LaborMode.INCOME_GOAL:
            if not self.income_goal or not self.work_hours_per_day:
                return Decimal('0')
            hours = self.work_hours_per_day * Decimal('22')
            return (self.income_goal / hours).quantize(Decimal("0.01"))
        
        