import uuid

import pytest
from rest_framework.test import APIClient

from apps.alerts.models import Alert


@pytest.mark.django_db
class TestAlertAPI:
    def test_list(self):
        Alert.objects.create(
            workspace_id=uuid.uuid4(), type=Alert.Type.MATERIAL_LOW,
            title="X",
        )
        client = APIClient()
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_mark_read(self):
        a = Alert.objects.create(
            workspace_id=uuid.uuid4(), type=Alert.Type.MATERIAL_LOW,
            title="X",
        )
        client = APIClient()
        response = client.post(f"/api/v1/alerts/{a.id}/mark_read/")
        assert response.status_code == 200
        a.refresh_from_db()
        assert a.is_read is True