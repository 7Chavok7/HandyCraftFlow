# core/apps/production/models.py
from django.db import models


from apps.catalog.models import ProductVariant
from apps.materials.models import MaterialBatch, MaterialType


class ProductionProfile(models.Model):
    """Профиль производства: обобщенный (3D печать, пошив, варка...)"""

    class EquipmentTypeHint(models.TextChoices):
        PRINTER_3D = 'printer_3d', '3D-принтер'
        SEWING = 'sewing', 'Швейная машинка'
        OTHER = 'other', 'Прочее'
    
    workspace_id = models.UUIDField(
        'ID кабинета',
        db_index=True,
    )
    name = models.CharField(
        "Название", 
        max_length=150
    )
    equipment_type_hint = models.CharField(
        "Подсказка типа оборудования", 
        max_length=20,
        choices=EquipmentTypeHint.choices, 
        default=EquipmentTypeHint.PRINTER_3D,
    )
    expected_duration_min = models.PositiveIntegerField(
        "Ожидаемое время, мин", 
        default=0,
    )
    expected_material_weight = models.DecimalField(
        "Ожидаемый вес материала, г", 
        max_digits=12, 
        decimal_places=3,
        null=True, 
        blank=True,
    )
    source_file = models.FileField(
        "Файл профиля (.3mf/.gcode/.pdf/.dxf)", 
        upload_to="profiles/",
        blank=True,
    )
    deviations_count = models.PositiveIntegerField(
        "Расхождений с фактом", 
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Профиль производства"
        verbose_name_plural = "Профили производства"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductionAsset(models.Model):
    """Исходник (геометрия/выкройка/чертёж) с версией и лицензией."""

    class Source(models.TextChoices):
        MAKERWORLD = "makerworld", "MakerWorld"
        PATREON = "patreon", "Patreon"
        CULTS3D = "cults3d", "Cults3D"
        OWN = "own", "Своя"
        CLIENT = "client", "От клиента"

    class LicenseStatus(models.TextChoices):
        COMMERCIAL_OK = "commercial_ok", "Можно продавать"
        NON_COMMERCIAL = "non_commercial", "Только для себя"
        SUBSCRIPTION = "subscription", "По подписке"
        UNKNOWN = "unknown", "Неизвестно"

    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name="assets",
    )
    source = models.CharField(
        "Источник", 
        max_length=20, 
        choices=Source.choices, 
        default=Source.OWN,
    )
    external_url = models.URLField("Ссылка на источник", blank=True)
    file = models.FileField(
        "Файл", 
        upload_to="assets/", 
        blank=True,
    )
    license_type = models.CharField("Тип лицензии", max_length=50, blank=True)
    license_status = models.CharField(
        "Статус лицензии", 
        max_length=20,
        choices=LicenseStatus.choices, 
        default=LicenseStatus.UNKNOWN,
    )
    version = models.CharField(
        "Версия", 
        max_length=20, 
        default="1"
    )
    imported_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Исходник"
        verbose_name_plural = "Исходники"
        ordering = [
            "variant", 
            "-imported_at"
        ]

    def __str__(self):
        return f"{self.variant} · {self.get_source_display()} · v{self.version}"


class Recipe(models.Model):
    """Рецепт производства варианта (BOM)."""

    class NormsSource(models.TextChoices):
        MANUAL = "manual", "Вручную"
        GCODE = "gcode", "Из gcode"
        THREEMF = "3mf", "Из .3mf"

    variant = models.OneToOneField(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name="recipe",
    )
    profile = models.ForeignKey(
        ProductionProfile, 
        on_delete=models.PROTECT,
        null=True, 
        blank=True, 
        related_name="recipes",
    )
    labor_minutes = models.PositiveIntegerField(
        "Труд, мин", 
        default=0,
    )
    norms_source = models.CharField(
        "Источник норм",
        max_length=20,
        choices=NormsSource.choices, 
        default=NormsSource.MANUAL,
    )
    avg_cost_cached = models.DecimalField(
        "Средняя себестоимость (кэш), ₽", 
        max_digits=12, 
        decimal_places=2,
        null=True, 
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"Рецепт: {self.variant}"


class RecipeLine(models.Model):
    """Строка рецепта: сколько материала на единицу."""

    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name="lines",
    )
    material_type = models.ForeignKey(
        MaterialType, 
        on_delete=models.PROTECT, 
        related_name="recipe_lines",
    )
    qty_per_unit = models.DecimalField(
        "Количество на единицу", 
        max_digits=12, 
        decimal_places=3,
    )
    waste_percent = models.DecimalField(
        "Процент на брак", 
        max_digits=5, 
        decimal_places=2, 
        default=0,
    )

    class Meta:
        verbose_name = "Строка рецепта"
        verbose_name_plural = "Строки рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recipe", 
                    "material_type"
                ],
                name="unique_material_per_recipe",
            ),
        ]

    def __str__(self):
        return f"{self.material_type}: {self.qty_per_unit} (+{self.waste_percent}%)"


class ProductionJob(models.Model):
    """Производственное задание (печать/пошив/варка)."""

    class Status(models.TextChoices):
        QUEUED = "queued", "В очереди"
        ASSIGNED = "assigned", "Назначено"
        PRINTING = "printing", "В работе"
        DONE = "done", "Завершено"
        CANCELLED = "cancelled", "Отменено"
        ERROR = "error", "Ошибка"

    workspace_id = models.UUIDField("ID кабинета", db_index=True)
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.PROTECT, 
        related_name="production_jobs",
    )
    profile = models.ForeignKey(
        ProductionProfile, 
        on_delete=models.PROTECT,
        null=True, 
        blank=True, 
        related_name="jobs",
    )
    material_batch = models.ForeignKey(
        MaterialBatch, 
        on_delete=models.PROTECT,
        null=True, 
        blank=True, 
        related_name="production_jobs",
    )
    equipment_id = models.UUIDField(
        "ID оборудования (из Farm)", 
        null=True, 
        blank=True, 
        db_index=True,
    )
    qty_planned = models.PositiveIntegerField(
        "План, шт", 
        default=1,
    )
    qty_done = models.PositiveIntegerField(
        "Готово, шт", 
        default=0,
    )
    qty_waste = models.PositiveIntegerField(
        "Брак, шт", 
        default=0,
    )
    expected_weight = models.DecimalField(
        "Ожидаемый вес, г", 
        max_digits=12, 
        decimal_places=3, 
        null=True, 
        blank=True,
    )
    expected_time_min = models.PositiveIntegerField(
        "Ожидаемое время, мин", 
        null=True, 
        blank=True,
    )
    actual_weight = models.DecimalField(
        "Фактический вес, г", 
        max_digits=12, 
        decimal_places=3, 
        null=True, 
        blank=True,
    )
    actual_time_min = models.PositiveIntegerField(
        "Фактическое время, мин", 
        null=True, 
        blank=True,
    )
    status = models.CharField(
        "Статус", 
        max_length=20, 
        choices=Status.choices, 
        default=Status.QUEUED,
    )
    comment = models.TextField(
        "Комментарий", 
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    started_at = models.DateTimeField(
        null=True, 
        blank=True
    )
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Производственное задание"
        verbose_name_plural = "Производственные задания"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace_id", "status"]),
            models.Index(fields=["variant", "-created_at"]),
        ]

    def __str__(self):
        return f"#{self.pk} {self.variant} ({self.get_status_display()})"