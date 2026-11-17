from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.promo.models import Promotion, PromotionItem
from apps.api.serializers.promo import PromotionSerializer, PromotionItemSerializer


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.prefetch_related("items")
    serializer_class = PromotionSerializer


class PromotionItemViewSet(viewsets.ModelViewSet):
    queryset = PromotionItem.objects.select_related("promotion", "variant")
    serializer_class = PromotionItemSerializer
    
    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        """Принять решение по акции: accepted / declined."""
        item = self.get_object()
        decision = request.data.get("decision")
        if decision not in ("accepted", "declined", "pending"):
            return Response({"error": "invalid decision"}, status=400)
        item.decision = decision
        item.decided_at = timezone.now()
        item.save(update_fields=["decision", "decided_at"])
        return Response(PromotionItemSerializer(item).data)
    
    @action(detail=True, methods=["get"])
    def forecast(self, request, pk=None):
        """Прогноз маржи: margin_at_proposed, snapshot_cost."""
        item = self.get_object()
        marketplace = item.promotion.marketplace
        price = item.proposed_price
        from apps.economics.services import calculate_cost, calculate_margin
        cost = calculate_cost(item.variant)
        margin = calculate_margin(item.variant, price, marketplace)
        item.margin_at_proposed = margin
        item.snapshot_cost = cost
        item.save(update_fields=["margin_at_proposed", "snapshot_cost"])
        return Response({
            "variant": item.variant.name,
            "proposed_price": str(price),
            "cost": str(cost),
            "margin": str(margin),
            "is_loss": margin < 0,
        })