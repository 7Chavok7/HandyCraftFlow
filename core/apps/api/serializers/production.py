from rest_framework import serializers

from apps.production.models import (
    ProductionProfile, ProductionAsset, Recipe, RecipeLine, ProductionJob,
)


class ProductionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionProfile
        fields = [
            "id", "name", "equipment_type_hint",
            "expected_duration_min", "expected_material_weight",
            "source_file", "deviations_count", "created_at",
        ]


class ProductionAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionAsset
        fields = [
            "id", "variant", "source", "external_url", "file",
            "license_type", "license_status", "version", "imported_at",
        ]


class RecipeLineSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)

    class Meta:
        model = RecipeLine
        fields = [
            "id", "material_type", "material_type_name",
            "qty_per_unit", "waste_percent",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    lines = RecipeLineSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id", "variant", "profile", "labor_minutes",
            "norms_source", "avg_cost_cached", "lines", "updated_at",
        ]


class ProductionJobSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source="variant.name", read_only=True)

    class Meta:
        model = ProductionJob
        fields = [
            "id", "variant", "variant_name", "profile", "material_batch",
            "equipment_id", "qty_planned", "qty_done", "qty_waste",
            "expected_weight", "expected_time_min",
            "actual_weight", "actual_time_min",
            "status", "comment",
            "created_at", "started_at", "finished_at",
        ]