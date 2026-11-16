from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.warehouse.models import (
    SellerAccount, 
    Warehouse, 
    Stock, 
    StockLedger,
)
from apps.api.serializers.warehouse import (
    SellerAccountSerializer, 
    WarehouseSerializer,
    StockSerializer, 
    StockLedgerSerializer,
)
from apps.warehouse.services import (
    adjust_stock, 
    reserve_stock, 
    unreserve_stock,
)


class SellerAccountViewSet(viewsets.ModelViewSet):
    queryset = SellerAccount.objects.all()
    serializer_class = SellerAccountSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.select_related("seller_account")
    serializer_class = WarehouseSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related("variant", "warehouse")
    serializer_class = StockSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        warehouse_id = self.request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        return qs

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        """Инвентаризация: установить фактический остаток."""
        stock = self.get_object()
        new_qty = request.data.get("new_qty")
        comment = request.data.get("comment", "")
        if new_qty is None:
            return Response({"error": "new_qty required"}, status=400)
        try:
            adjust_stock(stock=stock, new_qty=Decimal(new_qty), comment=comment)
        except (ValueError, ArithmeticError) as exc:
            return Response({"error": str(exc)}, status=400)
        stock.refresh_from_db()
        return Response(StockSerializer(stock).data)

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        stock = self.get_object()
        qty = request.data.get("qty")
        if qty is None:
            return Response({"error": "qty required"}, status=400)
        try:
            reserve_stock(stock=stock, qty=Decimal(qty),
                          comment=request.data.get("comment", ""))
        except (ValueError, ArithmeticError) as exc:
            return Response({"error": str(exc)}, status=400)
        stock.refresh_from_db()
        return Response(StockSerializer(stock).data)

    @action(detail=True, methods=["post"])
    def unreserve(self, request, pk=None):
        stock = self.get_object()
        qty = request.data.get("qty")
        if qty is None:
            return Response({"error": "qty required"}, status=400)
        try:
            unreserve_stock(stock=stock, qty=Decimal(qty),
                            comment=request.data.get("comment", ""))
        except (ValueError, ArithmeticError) as exc:
            return Response({"error": str(exc)}, status=400)
        stock.refresh_from_db()
        return Response(StockSerializer(stock).data)


class StockLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockLedger.objects.select_related("variant", "warehouse")
    serializer_class = StockLedgerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        variant_id = self.request.query_params.get("variant")
        if variant_id:
            qs = qs.filter(variant_id=variant_id)
        warehouse_id = self.request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        return qs