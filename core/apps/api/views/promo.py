from rest_framework import viewsets

from apps.promo.models import Promotion, PromotionItem
from apps.api.serializers.promo import PromotionSerializer, PromotionItemSerializer


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.prefetch_related("items")
    serializer_class = PromotionSerializer


class PromotionItemViewSet(viewsets.ModelViewSet):
    queryset = PromotionItem.objects.select_related("promotion", "variant")
    serializer_class = PromotionItemSerializer