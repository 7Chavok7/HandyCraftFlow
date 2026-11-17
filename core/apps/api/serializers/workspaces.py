from rest_framework import serializers

from apps.workspaces.models import WorkspaceSettings


class WorkspaceSettingsSerializer(serializers.ModelSerializer):
    effective_labor_rate = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True,
    )
    workspace_name = serializers.CharField(
        source="workspace.name", read_only=True,
    )

    class Meta:
        model = WorkspaceSettings
        fields = [
            "workspace", 
            "workspace_name",
            "labor_mode", 
            "labor_rate", 
            "income_goal", 
            "work_hours_per_day",
            "target_margin_percent", 
            "electricity_rate", 
            "tax_rate",
            "equipment_hour_cost",
            "effective_labor_rate",
        ]
        read_only_fields = ["workspace"]