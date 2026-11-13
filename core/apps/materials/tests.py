# core/apps/materials/tests.py
# core/apps/materials/tests.py
import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.guide.models import Unit, Color, Country, Manufacturer
from apps.materials.models import MaterialType, MaterialBatch, MaterialLedger


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def unit_gram(db):
    return Unit.objects.create(name="Грамм", short_name="г")


@pytest.fixture
def color_black(db):
    return Color.objects.create(name="Чёрный", ral_code="9005")


@pytest.fixture
def manufacturer_bambu(db):
    country = Country.objects.create(name="Китай")
    return Manufacturer.objects.create(name="Bambu Lab", country=country)


@pytest.fixture
def material_type(db, workspace_id, unit_gram, color_black):
    return MaterialType.objects.create(
        workspace_id=workspace_id,
        name="PLA чёрный",
        kind=MaterialType.Kind.RAW,
        unit=unit_gram,
        color=color_black,
        polymer="PLA",
    )


@pytest.fixture
def batch(db, material_type, manufacturer_bambu):
    return MaterialBatch.objects.create(
        material_type=material_type,
        manufacturer=manufacturer_bambu,
        qty_initial=Decimal("1000"),
        qty_remaining=Decimal("1000"),
        unit_cost=Decimal("1.2000"),
        purchased_at=date(2025, 1, 1),
    )


@pytest.mark.django_db
class TestMaterialType:
    def test_str(self, material_type):
        assert str(material_type) == "PLA чёрный"

    def test_unique_name_per_workspace(self, workspace_id, material_type):
        with pytest.raises(IntegrityError):
            MaterialType.objects.create(
                workspace_id=workspace_id,
                name="PLA чёрный",
                unit=material_type.unit,
            )

    def test_same_name_different_workspace(
        self, material_type, unit_gram,
    ):
        other_ws = uuid.uuid4()
        mt = MaterialType.objects.create(
            workspace_id=other_ws, name="PLA чёрный", unit=unit_gram,
        )
        assert mt.pk != material_type.pk

    def test_color_optional(self, workspace_id, unit_gram):
        mt = MaterialType.objects.create(
            workspace_id=workspace_id, name="Воск", unit=unit_gram,
        )
        assert mt.color is None


@pytest.mark.django_db
class TestMaterialBatch:
    def test_str(self, batch):
        assert "Bambu Lab" in str(batch)
        assert "01.01.2025" in str(batch)

    def test_manufacturer_optional(self, material_type):
        b = MaterialBatch.objects.create(
            material_type=material_type,
            qty_initial=Decimal("100"),
            qty_remaining=Decimal("100"),
            unit_cost=Decimal("0.05"),
            purchased_at=date(2025, 1, 1),
        )
        assert b.manufacturer is None
        assert "?" in str(b)

    def test_qty_remaining_non_negative(self, material_type):
        with pytest.raises(IntegrityError):
            MaterialBatch.objects.create(
                material_type=material_type,
                qty_initial=Decimal("100"),
                qty_remaining=Decimal("-1"),
                unit_cost=Decimal("1"),
                purchased_at=date(2025, 1, 1),
            )

    def test_qty_remaining_can_exceed_initial_after_adjustment(
        self, material_type,
    ):
        b = MaterialBatch.objects.create(
            material_type=material_type,
            qty_initial=Decimal("100"),
            qty_remaining=Decimal("105"),
            unit_cost=Decimal("1"),
            purchased_at=date(2025, 1, 1),
        )
        assert b.qty_remaining == Decimal("105")


@pytest.mark.django_db
class TestMaterialLedger:
    def test_str_positive(self, workspace_id, material_type, batch):
        entry = MaterialLedger.objects.create(
            workspace_id=workspace_id,
            material_type=material_type,
            batch=batch,
            movement_type=MaterialLedger.MovementType.INCOME,
            qty=Decimal("1000"),
        )
        assert "+1000" in str(entry)
        assert "Поступление" in str(entry)

    def test_str_negative(self, workspace_id, material_type, batch):
        entry = MaterialLedger.objects.create(
            workspace_id=workspace_id,
            material_type=material_type,
            batch=batch,
            movement_type=MaterialLedger.MovementType.TO_PRODUCTION,
            qty=Decimal("-12"),
        )
        assert "-12" in str(entry)
        assert "В производство" in str(entry)

    def test_batch_optional(self, workspace_id, material_type):
        entry = MaterialLedger.objects.create(
            workspace_id=workspace_id,
            material_type=material_type,
            movement_type=MaterialLedger.MovementType.ADJUSTMENT,
            qty=Decimal("-20"),
            comment="инвентаризация",
        )
        assert entry.batch is None

    def test_write_off_value(self):
        assert MaterialLedger.MovementType.WRITE_OFF.value == "write_off"