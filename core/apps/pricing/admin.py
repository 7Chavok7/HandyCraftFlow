# core/apps/pricing/admin.py
from django.contrib import admin
from .models import PriceRule, PriceHistory,MarketplaceFee


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    list_display = (
        "variant", "strategy", "min_margin_percent",
        "target_margin_percent", "fixed_price",
    )
    list_filter = ("strategy",)
    search_fields = ("variant__name", "variant__product__name")


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "variant", "price", "source", "comment")
    list_filter = ("source",)
    search_fields = ("variant__name", "variant__product__name", "comment")
    readonly_fields = ("variant", "price", "source", "comment", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    
@admin.register(MarketplaceFee)
class MarketplaceFeeAdmin(admin.ModelAdmin):
    list_display = (
        "marketplace", "category", "commission_percent",
        "logistics_cost", "valid_from", "valid_to",
    )
    list_filter = ("marketplace",)