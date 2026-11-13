from rest_framework import viewsets

from apps.pricing.models import PriceRule, PriceHistory, MarketplaceFee
from apps.api.serializers.pricing import (
    PriceRuleSerializer, PriceHistorySerializer, MarketplaceFeeSerializer,
)


class PriceRuleViewSet(viewsets.ModelViewSet):
    queryset = PriceRule.objects.select_related("variant")
    serializer_class = PriceRuleSerializer


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceHistory.objects.select_related("variant")
    serializer_class = PriceHistorySerializer


class MarketplaceFeeViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceFee.objects.select_related("category")
    serializer_class = MarketplaceFeeSerializer