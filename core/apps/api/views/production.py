from rest_framework import viewsets

from apps.production.models import (
    ProductionProfile, ProductionAsset, Recipe, RecipeLine, ProductionJob,
)
from apps.api.serializers.production import (
    ProductionProfileSerializer, ProductionAssetSerializer,
    RecipeSerializer, RecipeLineSerializer, ProductionJobSerializer,
)


class ProductionProfileViewSet(viewsets.ModelViewSet):
    queryset = ProductionProfile.objects.all()
    serializer_class = ProductionProfileSerializer


class ProductionAssetViewSet(viewsets.ModelViewSet):
    queryset = ProductionAsset.objects.select_related("variant")
    serializer_class = ProductionAssetSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("variant", "profile").prefetch_related("lines")
    serializer_class = RecipeSerializer


class RecipeLineViewSet(viewsets.ModelViewSet):
    queryset = RecipeLine.objects.select_related("recipe", "material_type")
    serializer_class = RecipeLineSerializer


class ProductionJobViewSet(viewsets.ModelViewSet):
    queryset = ProductionJob.objects.select_related("variant", "profile")
    serializer_class = ProductionJobSerializer