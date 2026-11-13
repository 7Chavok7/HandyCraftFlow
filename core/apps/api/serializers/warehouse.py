from rest_framework import serializers

from apps.warehouse.models import SellerAccount, Warehouse, Stock, StockLedger


class SellerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAccount
        fields = [
            "id", "marketplace", "name", "client_id",
            "is_active", "last_sync_at", "created_at",
        ]


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "id", "name", "type", "seller_account", "is_active", "created_at",
        ]


class StockSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    available_qty = serializers.DecimalField(
        max_digits=12, decimal_places=3, read_only=True,
    )

    class Meta:
        model = Stock
        fields = [
            "id", "variant", "variant_name", "warehouse",
            "qty", "reserved_qty", "available_qty", "updated_at",
        ]


class StockLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLedger
        fields = [
            "id", "variant", "warehouse", "movement_type",
            "qty", "comment", "created_at",
        ]