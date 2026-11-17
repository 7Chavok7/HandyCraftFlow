from rest_framework import serializers

from apps.catalog.models import Category, Product, ProductVariant, PlatformListing


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent", "path", "depth", "is_active"]


class ProductVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id", "product", "product_name", "name", "color",
            "vendor_code", "barcode", "extra_cost", "is_active", "image",
        ]
        read_only_fields = ["id"]



class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "workspace_id", "name", "category", "description",
            "is_active", "variants", "created_at", "image",
        ]


class PlatformListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformListing
        fields = [
            "id", "variant", "marketplace", "platform_sku",
            "url", "status", "last_sync_at",
        ]