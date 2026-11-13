# core/apps/production/admin.py
from django.contrib import admin
from .models import (
    ProductionProfile, ProductionAsset, Recipe, RecipeLine, ProductionJob,
)


class RecipeLineInline(admin.TabularInline):
    model = RecipeLine
    extra = 0


@admin.register(ProductionProfile)
class ProductionProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name", "equipment_type_hint", "expected_duration_min",
        "expected_material_weight", "deviations_count",
    )
    list_filter = ("equipment_type_hint",)
    search_fields = ("name",)


@admin.register(ProductionAsset)
class ProductionAssetAdmin(admin.ModelAdmin):
    list_display = ("variant", "source", "license_status", "version", "imported_at")
    list_filter = ("source", "license_status")
    search_fields = ("variant__name", "variant__product__name")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("variant", "profile", "labor_minutes", "norms_source", "avg_cost_cached")
    list_filter = ("norms_source",)
    search_fields = ("variant__name", "variant__product__name")
    inlines = [RecipeLineInline]


@admin.register(RecipeLine)
class RecipeLineAdmin(admin.ModelAdmin):
    list_display = ("recipe", "material_type", "qty_per_unit", "waste_percent")
    list_filter = ("material_type",)


@admin.register(ProductionJob)
class ProductionJobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "variant", "status", "qty_planned", "qty_done", "qty_waste",
        "equipment_id", "created_at",
    )
    list_filter = ("status",)
    search_fields = ("variant__name", "variant__product__name", "comment")
    readonly_fields = ("created_at", "started_at", "finished_at")