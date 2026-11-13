import uuid

import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductVariant


@pytest.mark.django_db
class TestProductsAPI:
    def test_list_with_variants(self):
        ws = uuid.uuid4()
        p = Product.objects.create(workspace_id=ws, name="Органайзер")
        ProductVariant.objects.create(product=p, name="Зелёный")
        client = APIClient()
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        results = response.data["results"]
        assert results[0]["name"] == "Органайзер"
        assert len(results[0]["variants"]) == 1