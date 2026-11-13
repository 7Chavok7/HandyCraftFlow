import pytest
from rest_framework.test import APIClient

from apps.guide.models import Unit


@pytest.mark.django_db
class TestUnitsAPI:
    def test_list(self):
        Unit.objects.create(name="Грамм", short_name="г")
        client = APIClient()
        response = client.get("/api/v1/units/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["short_name"] == "г"

    def test_create(self):
        client = APIClient()
        response = client.post("/api/v1/units/", {
            "name": "Килограмм", "short_name": "кг",
        })
        assert response.status_code == 201
        assert Unit.objects.count() == 1