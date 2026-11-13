import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Product, ProductVariant
from apps.guide.models import Unit
from apps.materials.models import MaterialType
from apps.production.models import (
    ProductionProfile, ProductionAsset, Recipe, RecipeLine, ProductionJob,
)


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def unit_gram(db):
    return Unit.objects.create(name="Грамм", short_name="г")


@pytest.fixture
def material_type(db, workspace_id, unit_gram):
    return MaterialType.objects.create(
        workspace_id=workspace_id, name="PLA чёрный", unit=unit_gram,
    )


@pytest.fixture
def variant(db, workspace_id):
    product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
    return ProductVariant.objects.create(product=product, name="Зелёный")


@pytest.fixture
def profile(db, workspace_id):
    return ProductionProfile.objects.create(
        workspace_id=workspace_id, name="Органайзер A1 0.2мм",
        expected_duration_min=45, expected_material_weight=Decimal("12.500"),
    )


@pytest.fixture
def recipe(db, variant, profile):
    return Recipe.objects.create(
        variant=variant, profile=profile, labor_minutes=5,
    )


# --- ProductionProfile ---

@pytest.mark.django_db
class TestProductionProfile:
    def test_str(self, profile):
        assert str(profile) == "Органайзер A1 0.2мм"

    def test_default_equipment_hint(self, workspace_id):
        p = ProductionProfile.objects.create(workspace_id=workspace_id, name="X")
        assert p.equipment_type_hint == ProductionProfile.EquipmentTypeHint.PRINTER_3D

    def test_default_deviations_zero(self, profile):
        assert profile.deviations_count == 0


# --- ProductionAsset ---

@pytest.mark.django_db
class TestProductionAsset:
    def test_str(self, variant):
        a = ProductionAsset.objects.create(
            variant=variant, source=ProductionAsset.Source.MAKERWORLD, version="2",
        )
        assert "MakerWorld" in str(a)
        assert "v2" in str(a)

    def test_default_license_unknown(self, variant):
        a = ProductionAsset.objects.create(variant=variant)
        assert a.license_status == ProductionAsset.LicenseStatus.UNKNOWN

    def test_multiple_assets_per_variant(self, variant):
        ProductionAsset.objects.create(variant=variant, version="1")
        ProductionAsset.objects.create(variant=variant, version="2")
        assert variant.assets.count() == 2


# --- Recipe ---

@pytest.mark.django_db
class TestRecipe:
    def test_str(self, recipe, variant):
        assert str(recipe) == f"Рецепт: {variant}"

    def test_one_to_one_variant(self, recipe, variant):
        with pytest.raises(IntegrityError):
            Recipe.objects.create(variant=variant)

    def test_profile_optional(self, variant):
        r = Recipe.objects.create(variant=variant)
        assert r.profile is None


# --- RecipeLine ---

@pytest.mark.django_db
class TestRecipeLine:
    def test_str(self, recipe, material_type):
        line = RecipeLine.objects.create(
            recipe=recipe, material_type=material_type,
            qty_per_unit=Decimal("12"), waste_percent=Decimal("5"),
        )
        assert "PLA чёрный" in str(line)
        assert "12" in str(line)

    def test_unique_material_per_recipe(self, recipe, material_type):
        RecipeLine.objects.create(
            recipe=recipe, material_type=material_type, qty_per_unit=Decimal("12"),
        )
        with pytest.raises(IntegrityError):
            RecipeLine.objects.create(
                recipe=recipe, material_type=material_type, qty_per_unit=Decimal("20"),
            )


# --- ProductionJob ---

@pytest.mark.django_db
class TestProductionJob:
    def test_str(self, workspace_id, variant):
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant, qty_planned=10,
        )
        assert "Органайзер / Зелёный" in str(job)
        assert "В очереди" in str(job)

    def test_default_status_queued(self, workspace_id, variant):
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant,
        )
        assert job.status == ProductionJob.Status.QUEUED

    def test_equipment_id_optional(self, workspace_id, variant):
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant,
        )
        assert job.equipment_id is None

    def test_equipment_id_set(self, workspace_id, variant):
        eq_id = uuid.uuid4()
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant, equipment_id=eq_id,
        )
        assert job.equipment_id == eq_id

    def test_material_batch_optional(self, workspace_id, variant):
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant,
        )
        assert job.material_batch is None

    def test_default_qty(self, workspace_id, variant):
        job = ProductionJob.objects.create(
            workspace_id=workspace_id, variant=variant,
        )
        assert job.qty_planned == 1
        assert job.qty_done == 0
        assert job.qty_waste == 0