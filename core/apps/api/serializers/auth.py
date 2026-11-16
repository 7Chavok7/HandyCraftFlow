# core/apps/api/serializers/auth.py
from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"], password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Неверный логин или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Пользователь заблокирован")
        attrs["user"] = user
        return attrs


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    workspace_id = serializers.UUIDField(allow_null=True)
    workspace_name = serializers.CharField(allow_blank=True)