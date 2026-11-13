# core/apps/warehouse/admin.py
from django.contrib import admin
from .models import SellerAccount, Warehouse, Stock, StockLedger


@admin.register(SellerAccount)
class SellerAccountAdmin(admin.ModelAdmin):
    list_display = ("marketplace", "name", "is_active", "last_sync_at")
    list_filter = ("marketplace", "is_active")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "seller_account", "is_active")
    list_filter = ("type", "is_active")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("variant", "warehouse", "qty", "reserved_qty", "available_qty")
    list_filter = ("warehouse",)
    search_fields = ("variant__name", "variant__product__name")
    readonly_fields = ("updated_at",)


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ("created_at", "variant", "warehouse", "movement_type", "qty")
    list_filter = ("movement_type", "warehouse")
    search_fields = ("variant__name", "comment")
    readonly_fields = (
        "variant", "warehouse", "movement_type", "qty", "comment", "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False