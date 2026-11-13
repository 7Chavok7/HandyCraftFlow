from rest_framework import serializers

from apps.materials.models import MaterialType, MaterialBatch, MaterialLedger


class MaterialTypeSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.short_name", read_only=True)
    color_name = serializers.CharField(source="color.name", read_only=True)
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = MaterialType
        fields = [
            "id", "workspace_id", "name", "kind", "unit", "unit_name",
            "polymer", "color", "color_name", "density",
            "min_balance", "current_balance", "is_active",
        ]

    def get_current_balance(self, obj):
        from django.db.models import Sum
        agg = obj.batches.filter(is_exhausted=False).aggregate(
            total=Sum("qty_remaining"),
        )
        return float(agg["total"] or 0)


class MaterialBatchSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)

    class Meta:
        model = MaterialBatch
        fields = [
            "id", "material_type", "material_type_name",
            "manufacturer", "manufacturer_name", "supplier",
            "qty_initial", "qty_remaining", "unit_cost",
            "purchased_at", "is_exhausted",
        ]


class MaterialLedgerSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)

    class Meta:
        model = MaterialLedger
        fields = [
            "id", "material_type", "material_type_name",
            "movement_type", "qty", "unit_cost_snapshot",
            "comment", "created_at",
        ]