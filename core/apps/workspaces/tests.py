# core/apps/workspaces/tests.py
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.workspaces.models import Workspace, WorkspaceSettings


User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="seller", password="x")


@pytest.fixture
def workspace(user):
    return Workspace.objects.create(name="Моя мастерская", owner=user)


@pytest.mark.django_db
class TestWorkspace:
    def test_str(self, workspace):
        assert str(workspace) == "Моя мастерская"

    def test_owner_related_name(self, user, workspace):
        assert workspace in user.workspaces.all()


@pytest.mark.django_db
class TestEffectiveLaborRate:
    def test_ignore_labor(self, workspace):
        s = workspace.settings
        s.labor_mode = WorkspaceSettings.LaborMode.IGNORE_LABOR
        s.labor_rate = Decimal("500")
        s.save()
        assert s.effective_labor_rate == Decimal("0")

    def test_manual_rate(self, workspace):
        s = workspace.settings
        s.labor_mode = WorkspaceSettings.LaborMode.MANUAL_RATE
        s.labor_rate = Decimal("500")
        s.save()
        assert s.effective_labor_rate == Decimal("500")

    def test_manual_rate_none(self, workspace):
        s = workspace.settings
        s.labor_mode = WorkspaceSettings.LaborMode.MANUAL_RATE
        s.labor_rate = None
        s.save()
        assert s.effective_labor_rate == Decimal("0")

    def test_income_goal(self, workspace):
        s = workspace.settings
        s.labor_mode = WorkspaceSettings.LaborMode.INCOME_GOAL
        s.income_goal = Decimal("60000")
        s.work_hours_per_day = Decimal("6")
        s.save()
        assert s.effective_labor_rate == Decimal("454.55")

    def test_income_goal_without_goal(self, workspace):
        s = workspace.settings
        s.labor_mode = WorkspaceSettings.LaborMode.INCOME_GOAL
        s.income_goal = None
        s.save()
        assert s.effective_labor_rate == Decimal("0")

    def test_equipment_hour_cost_default(self, workspace):
        assert workspace.settings.equipment_hour_cost == Decimal("0")


@pytest.mark.django_db
class TestWorkspaceSettingsSignal:
    def test_settings_created_on_workspace_create(self, user):
        ws = Workspace.objects.create(name="Новый", owner=user)
        assert hasattr(ws, "settings")
        assert ws.settings.labor_mode == WorkspaceSettings.LaborMode.IGNORE_LABOR