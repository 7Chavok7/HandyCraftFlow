from rest_framework import viewsets

from apps.catalog.models import Category, Product, ProductVariant, PlatformListing
from apps.api.serializers.catalog import (
    CategorySerializer, ProductSerializer,
    ProductVariantSerializer, PlatformListingSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("variants")
    serializer_class = ProductSerializer


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product")
    serializer_class = ProductVariantSerializer


class PlatformListingViewSet(viewsets.ModelViewSet):
    queryset = PlatformListing.objects.select_related("variant")
    serializer_class = PlatformListingSerializer