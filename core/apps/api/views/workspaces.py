from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.workspaces.models import WorkspaceSettings
from apps.api.serializers.workspaces import WorkspaceSettingsSerializer


class WorkspaceSettingsViewSet(viewsets.ModelViewSet):
    """Настройки кабинета. Одна запись на Workspace (OneToOne)."""

    queryset = WorkspaceSettings.objects.select_related("workspace")
    serializer_class = WorkspaceSettingsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        workspace_id = self.request.query_params.get("workspace_id")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Текущие настройки (первый Workspace, MVP)."""
        ws = WorkspaceSettings.objects.first()
        if not ws:
            return Response({"error": "no settings"}, status=404)
        return Response(WorkspaceSettingsSerializer(ws).data)