# farm/apps/printers/admin.py
from django.contrib import admin
from .models import Printer, AmsSlot, FarmJob


class AmsSlotInline(admin.TabularInline):
    model = AmsSlot
    extra = 0


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "status", "ams_slots_count", "is_active")
    list_filter = ("status", "is_active")
    inlines = [AmsSlotInline]


@admin.register(AmsSlot)
class AmsSlotAdmin(admin.ModelAdmin):
    list_display = ("printer", "slot_number", "material_batch_id")
    

@admin.register(FarmJob)
class FarmJobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "production_job_id", "printer", "status",
        "qty_planned", "qty_done", "qty_waste", "created_at",
    )
    list_filter = ("status", "printer")
    search_fields = ("production_job_id", "comment")
    readonly_fields = ("created_at", "started_at", "finished_at")