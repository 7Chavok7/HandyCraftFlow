from rest_framework import serializers

from apps.alerts.models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            "id", "type", "severity", "title", "message",
            "related_object_id", "is_read", "created_at",
        ]