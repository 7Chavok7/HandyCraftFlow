# farm/apps/printers/serializers.py
from rest_framework import serializers

from .models import Printer, AmsSlot, FarmJob


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = [
            "id", "workspace_id", "name", "model", "ip_address",
            "serial", "ams_slots_count", "status", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AmsSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmsSlot
        fields = ["id", "printer", "slot_number", "material_batch_id"]


class FarmJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmJob
        fields = [
            "id", "workspace_id", "production_job_id",
            "printer", "ams_slot", "status",
            "qty_planned", "qty_done", "qty_waste",
            "actual_weight", "actual_time_min",
            "comment", "created_at", "started_at", "finished_at",
        ]
        read_only_fields = [
            "id", "created_at", "started_at", "finished_at",
            "status", "qty_done", "qty_waste",
            "actual_weight", "actual_time_min",
        ]


class FinishFarmJobSerializer(serializers.Serializer):
    qty_done = serializers.IntegerField(min_value=0)
    qty_waste = serializers.IntegerField(min_value=0, default=0)
    actual_weight = serializers.DecimalField(
        max_digits=12, decimal_places=3,
        required=False, allow_null=True,
    )
    actual_time_min = serializers.IntegerField(
        required=False, allow_null=True, min_value=0,
    )
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class AssignFarmJobSerializer(serializers.Serializer):
    printer_id = serializers.IntegerField()
    ams_slot_id = serializers.IntegerField(required=False, allow_null=True)