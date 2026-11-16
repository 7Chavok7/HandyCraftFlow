# core/apps/api/permissions.py
from django.conf import settings
from rest_framework.permissions import BasePermission


class HasInternalToken(BasePermission):
    """Проверка заголовка X-Internal-Token для внутренних вызовов Farm → Core."""

    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Token", "")
        expected = getattr(settings, "INTERNAL_API_TOKEN", "")
        return bool(expected) and token == expected