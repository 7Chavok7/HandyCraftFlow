from rest_framework import serializers

from apps.pricing.models import PriceRule, PriceHistory, MarketplaceFee


class PriceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRule
        fields = [
            "id", "variant", "strategy", "min_margin_percent",
            "target_margin_percent", "fixed_price", "updated_at",
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = [
            "id", "variant", "price", "source", "comment", "created_at",
        ]


class MarketplaceFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceFee
        fields = [
            "id", "marketplace", "category", "commission_percent",
            "logistics_cost", "valid_from", "valid_to",
        ]