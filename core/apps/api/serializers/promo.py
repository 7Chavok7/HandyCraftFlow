from rest_framework import serializers

from apps.promo.models import Promotion, PromotionItem


class PromotionItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source="variant.name", read_only=True)

    class Meta:
        model = PromotionItem
        fields = [
            "id", "promotion", "variant", "variant_name",
            "proposed_price", "margin_at_proposed", "snapshot_cost",
            "decision", "decided_at", "comment",
        ]


class PromotionSerializer(serializers.ModelSerializer):
    items = PromotionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Promotion
        fields = [
            "id", "workspace_id", "marketplace", "external_id", "name",
            "starts_at", "ends_at", "discount_percent", "items",
            "created_at",
        ]