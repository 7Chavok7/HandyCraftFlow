# farm/apps/printers/tests.py
import uuid

import pytest

from unittest.mock import patch, MagicMock

from apps.printers import services
from apps.printers.models import Printer, AmsSlot, FarmJob


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
        
        
@pytest.mark.django_db
class TestFarmJobServices:
    def test_start_from_assigned(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        services.start_job(farm_job=job)
        job.refresh_from_db()
        assert job.status == FarmJob.Status.PRINTING
        assert job.started_at is not None

    def test_start_from_done_raises(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
            status=FarmJob.Status.DONE,
        )
        with pytest.raises(ValueError):
            services.start_job(farm_job=job)

    def test_pause(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
            status=FarmJob.Status.PRINTING,
        )
        services.pause_job(farm_job=job)
        job.refresh_from_db()
        assert job.status == FarmJob.Status.PAUSED

    def test_cancel(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        services.cancel_job(farm_job=job, comment="сломался принтер")
        job.refresh_from_db()
        assert job.status == FarmJob.Status.CANCELLED
        assert "сломался принтер" in job.comment

    def test_finish(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
            status=FarmJob.Status.PRINTING,
        )
        services.finish_job(
            farm_job=job, qty_done=10, qty_waste=1,
            actual_weight=Decimal("12.5"), actual_time_min=45,
        )
        job.refresh_from_db()
        assert job.status == FarmJob.Status.DONE
        assert job.qty_done == 10
        assert job.qty_waste == 1
        assert job.finished_at is not None

    def test_finish_from_assigned_raises(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        with pytest.raises(ValueError):
            services.finish_job(farm_job=job, qty_done=1)


@pytest.mark.django_db
class TestFarmJobAPI:
    def _client(self):
        from rest_framework.test import APIClient
        return APIClient()

    def test_start_api(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        r = self._client().post(f"/farm/api/v1/jobs/{job.id}/start/")
        assert r.status_code == 200
        job.refresh_from_db()
        assert job.status == FarmJob.Status.PRINTING

    def test_finish_api(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
            status=FarmJob.Status.PRINTING,
        )
        r = self._client().post(
            f"/farm/api/v1/jobs/{job.id}/finish/",
            {"qty_done": 10, "qty_waste": 1, "actual_time_min": 45},
            format="json",
        )
        assert r.status_code == 200
        job.refresh_from_db()
        assert job.status == FarmJob.Status.DONE

    def test_cancel_api(self, workspace_id, printer_for_job):
        job = FarmJob.objects.create(
            workspace_id=workspace_id,
            production_job_id=uuid.uuid4(),
            printer=printer_for_job,
        )
        r = self._client().post(
            f"/farm/api/v1/jobs/{job.id}/cancel/",
            {"comment": "сломался"}, format="json",
        )
        assert r.status_code == 200
        job.refresh_from_db()
        assert job.status == FarmJob.Status.CANCELLED
        
        
@pytest.mark.django_db
class TestCoreClient:
    def test_send_report_ok(self, settings):
        settings.CORE_API_URL = "http://core-test"
        settings.INTERNAL_API_TOKEN = "secret"

        with patch("apps.printers.core_client.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text="ok")

            from apps.printers.core_client import send_report_to_core
            result = send_report_to_core(
                production_job_id="abc-123",
                qty_done=10,
                qty_waste=1,
                actual_weight="12.5",
                actual_time_min=45,
                comment="тест",
            )

            assert result is True
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs
            assert "http://core-test/api/v1/jobs/abc-123/report/" in mock_post.call_args.args
            assert call_kwargs["headers"]["X-Internal-Token"] == "secret"
            assert call_kwargs["json"]["qty_done"] == 10

    def test_send_report_http_error(self, settings):
        settings.CORE_API_URL = "http://core-test"
        settings.INTERNAL_API_TOKEN = "secret"

        with patch("apps.printers.core_client.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=400, text="bad")

            from apps.printers.core_client import send_report_to_core
            result = send_report_to_core(
                production_job_id="abc", qty_done=1,
            )
            assert result is False

    def test_send_report_network_error(self, settings):
        import requests
        settings.CORE_API_URL = "http://core-test"
        settings.INTERNAL_API_TOKEN = "secret"

        with patch("apps.printers.core_client.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("timeout")

            from apps.printers.core_client import send_report_to_core
            result = send_report_to_core(
                production_job_id="abc", qty_done=1,
            )
            assert result is False