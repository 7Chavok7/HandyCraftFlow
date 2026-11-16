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
        

# farm/apps/printers/tests.py — добавить в конец

from datetime import datetime, timezone
from decimal import Decimal

from apps.printers.models import FarmJob


@pytest.fixture
def printer_for_job(db, workspace_id):
    return Printer.objects.create(
        workspace_id=workspace_id,
        name="Bambu A1",
        model="A1",
    )


@pytest.fixture
def farm_job(db, workspace_id, printer_for_job):
    return FarmJob.objects.create(
        workspace_id=workspace_id,
        production_job_id=uuid.uuid4(),
        printer=printer_for_job,
        qty_planned=10,
    )


@pytest.mark.django_db
class TestFarmJob:
    def test_str(self, farm_job):
        assert "printer" in str(farm_job).lower()
        assert "Назначено" in str(farm_job)

    def test_default_status_assigned(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        assert job.status == FarmJob.Status.ASSIGNED

    def test_default_qty(self, farm_job):
        assert farm_job.qty_planned == 10
        assert farm_job.qty_done == 0
        assert farm_job.qty_waste == 0

    def test_production_job_id_unique(self, farm_job, workspace_id, printer_for_job):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            FarmJob.objects.create(
                workspace_id=workspace_id,
                production_job_id=farm_job.production_job_id,
                printer=printer_for_job,
            )

    def test_ams_slot_optional(self, farm_job):
        assert farm_job.ams_slot is None

    def test_actual_fields_optional(self, farm_job):
        assert farm_job.actual_weight is None
        assert farm_job.actual_time_min is None
        assert farm_job.started_at is None
        assert farm_job.finished_at is None