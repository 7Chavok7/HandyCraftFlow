# farm/apps/printers/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Printer, AmsSlot, FarmJob
from .serializers import (
    PrinterSerializer, AmsSlotSerializer, FarmJobSerializer,
    AssignFarmJobSerializer, FinishFarmJobSerializer,
)
from . import services


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer


class AmsSlotViewSet(viewsets.ModelViewSet):
    queryset = AmsSlot.objects.select_related("printer")
    serializer_class = AmsSlotSerializer


class FarmJobViewSet(viewsets.ModelViewSet):
    queryset = FarmJob.objects.select_related("printer", "ams_slot")
    serializer_class = FarmJobSerializer

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        job = self.get_object()
        s = AssignFarmJobSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        printer = Printer.objects.get(pk=s.validated_data["printer_id"])
        ams = None
        if s.validated_data.get("ams_slot_id"):
            ams = AmsSlot.objects.get(pk=s.validated_data["ams_slot_id"])
        services.assign_job(farm_job=job, printer=printer, ams_slot=ams)
        return Response(FarmJobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        job = self.get_object()
        try:
            services.start_job(farm_job=job)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(FarmJobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        job = self.get_object()
        try:
            services.pause_job(farm_job=job)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(FarmJobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        job = self.get_object()
        try:
            services.cancel_job(farm_job=job, comment=request.data.get("comment", ""))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(FarmJobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        job = self.get_object()
        s = FinishFarmJobSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            services.finish_job(
                farm_job=job,
                qty_done=s.validated_data["qty_done"],
                qty_waste=s.validated_data["qty_waste"],
                actual_weight=s.validated_data.get("actual_weight"),
                actual_time_min=s.validated_data.get("actual_time_min"),
                comment=s.validated_data.get("comment", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response(FarmJobSerializer(job).data)