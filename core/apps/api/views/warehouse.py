from rest_framework import viewsets

from apps.warehouse.models import SellerAccount, Warehouse, Stock, StockLedger
from apps.api.serializers.warehouse import (
    SellerAccountSerializer, WarehouseSerializer,
    StockSerializer, StockLedgerSerializer,
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


class StockLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockLedger.objects.select_related("variant", "warehouse")
    serializer_class = StockLedgerSerializer