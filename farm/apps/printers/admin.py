# farm/apps/printers/admin.py
from django.contrib import admin
from .models import Printer, AmsSlot


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