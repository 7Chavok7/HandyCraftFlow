# core/apps/workspace/admin.py
from django.contrib import admin
from .models import Workspace, WorkspaceSettings


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    readonly_fields = ("created_at",)


@admin.register(WorkspaceSettings)
class WorkspaceSettingsAdmin(admin.ModelAdmin):
    list_display = ("workspace", "labor_mode", "effective_labor_rate")
    fieldsets = (
        (None, {"fields": ("workspace",)}),
        ("Труд", {"fields": (
            "labor_mode", "labor_rate", "income_goal", "work_hours_per_day",
        )}),
        ("Экономика", {"fields": (
            "target_margin_percent", "electricity_rate", "tax_rate",
        )}),
    )
    readonly_fields = ("effective_labor_rate",)