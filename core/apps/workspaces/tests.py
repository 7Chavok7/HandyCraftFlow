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
        s = WorkspaceSettings.objects.create(
            workspace=workspace,
            labor_mode=WorkspaceSettings.LaborMode.IGNORE_LABOR,
            labor_rate=Decimal("500"),
        )
        assert s.effective_labor_rate == Decimal("0")

    def test_manual_rate(self, workspace):
        s = WorkspaceSettings.objects.create(
            workspace=workspace,
            labor_mode=WorkspaceSettings.LaborMode.MANUAL_RATE,
            labor_rate=Decimal("500"),
        )
        assert s.effective_labor_rate == Decimal("500")

    def test_manual_rate_none(self, workspace):
        s = WorkspaceSettings.objects.create(
            workspace=workspace,
            labor_mode=WorkspaceSettings.LaborMode.MANUAL_RATE,
            labor_rate=None,
        )
        assert s.effective_labor_rate == Decimal("0")

    def test_income_goal(self, workspace):
        s = WorkspaceSettings.objects.create(
            workspace=workspace,
            labor_mode=WorkspaceSettings.LaborMode.INCOME_GOAL,
            income_goal=Decimal("60000"),
            work_hours_per_day=Decimal("6"),
        )
        # 60000 / (6 * 22) = 454.54...
        assert s.effective_labor_rate == Decimal("454.55")

    def test_income_goal_without_goal(self, workspace):
        s = WorkspaceSettings.objects.create(
            workspace=workspace,
            labor_mode=WorkspaceSettings.LaborMode.INCOME_GOAL,
            income_goal=None,
        )
        assert s.effective_labor_rate == Decimal("0")
