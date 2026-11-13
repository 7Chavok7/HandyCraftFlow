from django.contrib import admin
from .models import Promotion, PromotionItem


class PromotionItemInline(admin.TabularInline):
    model = PromotionItem
    extra = 0
    readonly_fields = ("margin_at_proposed", "snapshot_cost", "decided_at")


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "marketplace", "starts_at", "ends_at", "discount_percent")
    list_filter = ("marketplace",)
    search_fields = ("name", "external_id")
    inlines = [PromotionItemInline]


@admin.register(PromotionItem)
class PromotionItemAdmin(admin.ModelAdmin):
    list_display = (
        "promotion", "variant", "proposed_price", "margin_at_proposed",
        "decision",
    )
    list_filter = ("decision", "promotion__marketplace")
    search_fields = ("variant__name", "variant__product__name")