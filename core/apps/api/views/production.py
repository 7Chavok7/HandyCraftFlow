from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.production.models import (
    ProductionProfile, 
    ProductionAsset, 
    Recipe, 
    RecipeLine, 
    ProductionJob,
)
from apps.api.serializers.production import (
    ProductionProfileSerializer, 
    ProductionAssetSerializer,
    RecipeSerializer, 
    RecipeLineSerializer, 
    ProductionJobSerializer,
    ProductionJobReportSerializer,
)
from apps.api.permissions import HasInternalToken
from apps.production.services import complete_production_job


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
    

class ProductionJobViewSet(viewsets.ModelViewSet):
    queryset = ProductionJob.objects.select_related("variant", "profile")
    serializer_class = ProductionJobSerializer

    @action(detail=True, methods=["post"], permission_classes=[HasInternalToken])
    def report(self, request, pk=None):
        """Farm сообщает факт: списание материала + поступление изделий."""
        job = self.get_object()
        serializer = ProductionJobReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            complete_production_job(
                job=job,
                qty_done=serializer.validated_data["qty_done"],
                qty_waste=serializer.validated_data["qty_waste"],
                actual_weight=serializer.validated_data.get("actual_weight"),
                actual_time_min=serializer.validated_data.get("actual_time_min"),
                comment=serializer.validated_data.get("comment", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)

        return Response(ProductionJobSerializer(job).data)
    
    
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Завершить задание вручную (фронт, если Farm недоступен)."""
        job = self.get_object()
        serializer = ProductionJobReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            complete_production_job(
                job=job,
                qty_done=serializer.validated_data["qty_done"],
                qty_waste=serializer.validated_data["qty_waste"],
                actual_weight=serializer.validated_data.get("actual_weight"),
                actual_time_min=serializer.validated_data.get("actual_time_min"),
                comment=serializer.validated_data.get("comment", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)

        return Response(ProductionJobSerializer(job).data)