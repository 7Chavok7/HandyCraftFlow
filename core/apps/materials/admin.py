# core/apps/materials/admin.py
from django.contrib import admin
from .models import MaterialType, MaterialBatch, MaterialLedger


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "unit", "min_balance", "is_active")
    list_filter = ("kind", "unit", "is_active")
    search_fields = ("name", "polymer", "color")


class MaterialLedgerInline(admin.TabularInline):
    model = MaterialLedger
    extra = 0
    readonly_fields = (
        "movement_type", "qty", "unit_cost_snapshot", "comment", "created_at",
    )
    can_delete = False


@admin.register(MaterialBatch)
class MaterialBatchAdmin(admin.ModelAdmin):
    list_display = (
        "material_type", 
        "manufacturer", 
        "qty_remaining",
        "unit_cost", 
        "purchased_at", 
        "is_exhausted",
    )
    list_filter = ("is_exhausted", "manufacturer")
    readonly_fields = ("qty_remaining", "is_exhausted")
    inlines = [MaterialLedgerInline]


@admin.register(MaterialLedger)
class MaterialLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "material_type", "movement_type", "qty", "batch",
    )
    list_filter = ("movement_type",)
    readonly_fields = (
        "workspace_id", "material_type", "batch", "movement_type",
        "qty", "unit_cost_snapshot", "comment", "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False