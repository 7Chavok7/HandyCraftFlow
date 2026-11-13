from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.alerts.models import Alert
from apps.economics.services import calculate_cost, min_price, profit_per_production_hour
from apps.production.models import ProductionJob
from apps.promo.models import PromotionItem
from apps.warehouse.models import Stock


class TodayDashboardView(APIView):
    """Экран «Сегодня»: сводка для селлера.

    Параметры запроса:
      ?workspace_id=<uuid>   (обязательный)
    """

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            return Response({"error": "workspace_id required"}, status=400)

        # Очередь производства
        queued_jobs = ProductionJob.objects.filter(
            workspace_id=workspace_id,
            status__in=[
                ProductionJob.Status.QUEUED,
                ProductionJob.Status.ASSIGNED,
                ProductionJob.Status.PRINTING,
            ],
        )[:10]

        # Акции, ожидающие решения
        pending_promos = PromotionItem.objects.filter(
            promotion__workspace_id=workspace_id,
            decision=PromotionItem.Decision.PENDING,
        ).select_related("promotion", "variant")[:10]

        # Заканчивается (остаток < 5)
        low_stocks = Stock.objects.filter(
            warehouse__workspace_id=workspace_id,
            qty__lt=5, qty__gt=0,
        ).select_related("variant", "warehouse")[:10]

        # Непрочитанные алерты
        unread_alerts = Alert.objects.filter(
            workspace_id=workspace_id, is_read=False,
        )[:20]

        return Response({
            "queued_jobs": [
                {
                    "id": str(j.id),
                    "variant": j.variant.name,
                    "qty_planned": j.qty_planned,
                    "status": j.status,
                }
                for j in queued_jobs
            ],
            "pending_promotions": [
                {
                    "id": str(p.id),
                    "promotion": p.promotion.name,
                    "variant": p.variant.name,
                    "proposed_price": str(p.proposed_price),
                    "decision": p.decision,
                }
                for p in pending_promos
            ],
            "low_stocks": [
                {
                    "variant": s.variant.name,
                    "warehouse": s.warehouse.name,
                    "qty": str(s.qty),
                    "available": str(s.available_qty),
                }
                for s in low_stocks
            ],
            "unread_alerts": [
                {
                    "id": str(a.id),
                    "type": a.type,
                    "severity": a.severity,
                    "title": a.title,
                }
                for a in unread_alerts
            ],
        })


class VariantEconomicsView(APIView):
    """Экономика варианта: cost / min_price / profit_per_hour на заданной цене.

    Параметры:
      ?variant_id=<uuid>&marketplace=wb&price=1000
    """

    def get(self, request):
        variant_id = request.query_params.get("variant_id")
        marketplace = request.query_params.get("marketplace", "wb")
        price_str = request.query_params.get("price", "0")

        if not variant_id:
            return Response({"error": "variant_id required"}, status=400)

        from apps.catalog.models import ProductVariant

        try:
            variant = ProductVariant.objects.get(pk=variant_id)
        except (ProductVariant.DoesNotExist, ValueError, TypeError):
            return Response({"error": "variant not found"}, status=404)

        price = Decimal(price_str)
        cost = calculate_cost(variant)
        minimum = min_price(variant, marketplace)
        per_hour = (
            profit_per_production_hour(variant, price, marketplace)
            if price > 0 else Decimal("0")
        )

        return Response({
            "variant_id": str(variant.id),
            "marketplace": marketplace,
            "cost": str(cost),
            "min_price": str(minimum),
            "price": str(price),
            "profit_per_production_hour": str(per_hour),
        })