from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.catalog.models import (
    Category, 
    Product, 
    ProductVariant, 
    PlatformListing,
)
from apps.api.serializers.catalog import (
    CategorySerializer, 
    ProductSerializer,
    ProductVariantSerializer, 
    PlatformListingSerializer,
)
from apps.api.serializers.production import RecipeSerializer
from apps.api.serializers.warehouse import StockSerializer
from apps.economics.services import (
    calculate_cost, 
    min_price, 
    profit_per_production_hour,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("variants")
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product")
    serializer_class = ProductVariantSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=True, methods=["get"], url_path="detail")
    def detail_view(self, request, pk=None):
        """Карточка варианта: рецепт, остатки, экономика."""
        variant = self.get_object()

        try:
            recipe = variant.recipe
            recipe_data = RecipeSerializer(recipe).data
        except Exception:
            recipe_data = None

        stocks = variant.stocks.select_related("warehouse")
        stocks_data = StockSerializer(stocks, many=True).data

        marketplace = request.query_params.get("marketplace", "wb")
        price_str = request.query_params.get("price", "0")
        try:
            price = Decimal(price_str)
        except Exception:
            price = Decimal("0")

        cost = calculate_cost(variant)
        minimum = min_price(variant, marketplace)
        per_hour = (
            profit_per_production_hour(variant, price, marketplace)
            if price > 0 else Decimal("0")
        )
        
        all_variants = ProductVariant.objects.filter(
            product=variant.product
        ).order_by("name")
        all_variants_data = ProductVariantSerializer(all_variants, many=True).data

        return Response({
            "variant": ProductVariantSerializer(variant).data,
            "all_variants": all_variants_data,
            "recipe": recipe_data,
            "stocks": stocks_data,
            "economics": {
                "marketplace": marketplace,
                "price": str(price),
                "cost": str(cost),
                "min_price": str(minimum),
                "profit_per_production_hour": str(per_hour),
            },
        })


class PlatformListingViewSet(viewsets.ModelViewSet):
    queryset = PlatformListing.objects.select_related("variant")
    serializer_class = PlatformListingSerializer