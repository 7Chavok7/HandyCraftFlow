# core/apps/api/views/auth.py
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.auth import LoginSerializer, MeSerializer
from apps.workspaces.models import Workspace


def _workspace_for_user(user):
    """Первый Workspace пользователя. MVP: один пользователь = один Workspace."""
    return Workspace.objects.filter(owner=user).first()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"ok": True, "username": user.username})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": True})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ws = _workspace_for_user(request.user)
        return Response(MeSerializer({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "workspace_id": ws.id if ws else None,
            "workspace_name": ws.name if ws else "",
        }).data)
        
        
class CsrfTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"csrfToken": get_token(request)})