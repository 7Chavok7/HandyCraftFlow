from rest_framework import viewsets

from apps.materials.models import MaterialType, MaterialBatch, MaterialLedger
from apps.api.serializers.materials import (
    MaterialTypeSerializer, MaterialBatchSerializer, MaterialLedgerSerializer,
)


class MaterialTypeViewSet(viewsets.ModelViewSet):
    queryset = MaterialType.objects.all()
    serializer_class = MaterialTypeSerializer


class MaterialBatchViewSet(viewsets.ModelViewSet):
    queryset = MaterialBatch.objects.select_related(
        "material_type", "manufacturer",
    )
    serializer_class = MaterialBatchSerializer


class MaterialLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialLedger.objects.select_related("material_type")
    serializer_class = MaterialLedgerSerializer