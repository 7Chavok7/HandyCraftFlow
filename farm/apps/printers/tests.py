# farm/apps/printers/tests.py
import uuid

import pytest

from apps.printers.models import Printer, AmsSlot


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def printer(db, workspace_id):
    return Printer.objects.create(
        workspace_id=workspace_id,
        name="Bambu A1 mini",
        model="A1 mini",
        ams_slots_count=4,
        status=Printer.Status.FREE,
    )


@pytest.mark.django_db
class TestPrinter:
    def test_str(self, printer):
        assert str(printer) == "Bambu A1 mini (A1 mini)"

    def test_default_status(self, workspace_id):
        p = Printer.objects.create(workspace_id=workspace_id, name="P1S")
        assert p.status == Printer.Status.OFFLINE

    def test_unique_name_per_workspace(self, workspace_id, printer):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Printer.objects.create(workspace_id=workspace_id, name="Bambu A1 mini")


@pytest.mark.django_db
class TestAmsSlot:
    def test_str(self, printer):
        slot = AmsSlot.objects.create(printer=printer, slot_number=1)
        assert str(slot) == "Bambu A1 mini · слот 1"

    def test_unique_slot_per_printer(self, printer):
        from django.db import IntegrityError
        AmsSlot.objects.create(printer=printer, slot_number=1)
        with pytest.raises(IntegrityError):
            AmsSlot.objects.create(printer=printer, slot_number=1)

    def test_material_batch_optional(self, printer):
        slot = AmsSlot.objects.create(printer=printer, slot_number=2)
        assert slot.material_batch_id is None