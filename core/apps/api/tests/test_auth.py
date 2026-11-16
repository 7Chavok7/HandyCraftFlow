import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.workspaces.models import Workspace

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="seller", password="secret123")


@pytest.fixture
def workspace_for_user(db, user):
    return Workspace.objects.create(name="Мастерская", owner=user)


@pytest.mark.django_db
class TestLogin:
    def test_login_ok(self, user):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "seller", "password": "secret123"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["ok"] is True

    def test_login_wrong_password(self, user):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "seller", "password": "wrong"},
            format="json",
        )
        assert response.status_code == 400

    def test_login_missing_fields(self):
        client = APIClient()
        response = client.post("/api/v1/auth/login/", {}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestMe:
    def test_me_unauthorized(self):
        client = APIClient()
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 403

    def test_me_authorized(self, user, workspace_for_user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["username"] == "seller"
        assert response.data["workspace_id"] == str(workspace_for_user.id)
        assert response.data["workspace_name"] == "Мастерская"


@pytest.mark.django_db
class TestLogout:
    def test_logout(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/logout/")
        assert response.status_code == 200