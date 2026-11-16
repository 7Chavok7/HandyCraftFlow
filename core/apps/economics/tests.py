import uuid
from datetime import date
from decimal import Decimal

import pytest

from apps.catalog.models import Product, ProductVariant, Category
from apps.guide.models import Unit, Country, Manufacturer
from apps.materials.models import MaterialType, MaterialBatch
from apps.pricing.models import PriceRule, MarketplaceFee
from apps.production.models import ProductionProfile, Recipe, RecipeLine
from apps.workspaces.models import Workspace, WorkspaceSettings
from apps.economics.services import (
    avg_material_cost, calculate_cost, calculate_margin,
    calculate_margin_percent, min_price, profit_per_production_hour,
)


@pytest.fixture
def workspace(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="seller", password="x")
    ws = Workspace.objects.create(name="Мастерская", owner=user)
    # settings создан сигналом
    ws.settings.labor_mode = WorkspaceSettings.LaborMode.MANUAL_RATE
    ws.settings.labor_rate = Decimal("500")
    ws.settings.tax_rate = Decimal("4")
    ws.settings.equipment_hour_cost = Decimal("20")
    ws.settings.save()
    return ws


@pytest.fixture
def unit_gram(db):
    return Unit.objects.create(name="Грамм", short_name="г")


@pytest.fixture
def manufacturer(db):
    c = Country.objects.create(name="Китай")
    return Manufacturer.objects.create(name="Bambu Lab", country=c)


@pytest.fixture
def material_type(db, workspace, unit_gram):
    return MaterialType.objects.create(
        workspace_id=workspace.id, name="PLA чёрный", unit=unit_gram,
    )


@pytest.fixture
def material_batch(db, material_type, manufacturer):
    return MaterialBatch.objects.create(
        material_type=material_type, manufacturer=manufacturer,
        qty_initial=Decimal("1000"), qty_remaining=Decimal("1000"),
        unit_cost=Decimal("1.5000"), purchased_at=date(2025, 1, 1),
    )


@pytest.fixture
def variant(db, workspace):
    cat = Category.objects.create(workspace_id=workspace.id, name="Декор")
    product = Product.objects.create(
        workspace_id=workspace.id, name="Органайзер", category=cat,
    )
    return ProductVariant.objects.create(product=product, name="Зелёный")


@pytest.fixture
def profile(db, workspace):
    return ProductionProfile.objects.create(
        workspace_id=workspace.id, name="Органайзер A1",
        expected_duration_min=45,
    )


@pytest.fixture
def recipe(db, variant, profile, material_type):
    r = Recipe.objects.create(variant=variant, profile=profile, labor_minutes=5)
    RecipeLine.objects.create(
        recipe=r, material_type=material_type,
        qty_per_unit=Decimal("12"), waste_percent=Decimal("5"),
    )
    return r


@pytest.fixture
def price_rule(db, variant):
    return PriceRule.objects.create(
        variant=variant, min_margin_percent=Decimal("15"),
        target_margin_percent=Decimal("35"),
    )


# --- avg_material_cost ---

@pytest.mark.django_db
class TestAvgMaterialCost:
    def test_returns_weighted_avg(self, material_type, material_batch):
        assert avg_material_cost(material_type) == Decimal("1.5000")

    def test_no_batches(self, material_type):
        assert avg_material_cost(material_type) == Decimal("0")

    def test_two_batches_weighted(self, material_type, manufacturer):
        MaterialBatch.objects.create(
            material_type=material_type, manufacturer=manufacturer,
            qty_initial=Decimal("1000"), qty_remaining=Decimal("1000"),
            unit_cost=Decimal("2.0000"), purchased_at=date(2025, 1, 1),
        )
        MaterialBatch.objects.create(
            material_type=material_type, manufacturer=manufacturer,
            qty_initial=Decimal("1000"), qty_remaining=Decimal("1000"),
            unit_cost=Decimal("1.0000"), purchased_at=date(2025, 2, 1),
        )
        # (1000*2 + 1000*1) / 2000 = 1.5
        assert avg_material_cost(material_type) == Decimal("1.5000")


# --- calculate_cost ---

@pytest.mark.django_db
class TestCalculateCost:
    def test_full_recipe(self, variant, recipe, material_batch, workspace):
        # материалы: 12 * 1.05 * 1.5 = 18.9
        # оборудование: 45/60 * 20 = 15
        # труд: 5/60 * 500 = 41.67
        # итого: 18.9 + 15 + 41.67 = 75.57
        cost = calculate_cost(variant)
        assert cost == Decimal("75.57")

    def test_no_recipe(self, variant):
        cost = calculate_cost(variant)
        assert cost == Decimal("0")

    def test_extra_cost_included(self, variant, recipe, material_batch):
        variant.extra_cost = Decimal("10")
        variant.save()
        cost = calculate_cost(variant)
        assert cost == Decimal("85.57")


# --- min_price ---

@pytest.mark.django_db
class TestMinPrice:
    def test_no_fee(self, variant, price_rule, recipe, material_batch, workspace):
        # cost=75.57, logistics=0, commission=0, tax=4%, min_margin=15%
        # denom = 1 - 0 - 0.04 - 0.15 = 0.81
        # price = (75.57 + 0) / 0.81 = 93.296... → 93.30
        p = min_price(variant, "wb")
        assert p == Decimal("93.30")

    def test_with_fee(self, variant, price_rule, recipe, material_batch, workspace):
        MarketplaceFee.objects.create(
            marketplace="wb", commission_percent=Decimal("20"),
            logistics_cost=Decimal("50"),
        )
        # denom = 1 - 0.2 - 0.04 - 0.15 = 0.61
        # price = (75.57 + 50) / 0.61 = 205.85...
        p = min_price(variant, "wb")
        assert p == Decimal("205.85")

    def test_impossible_margin_returns_zero(
        self, variant, price_rule, recipe, material_batch, workspace,
    ):
        MarketplaceFee.objects.create(
            marketplace="wb", commission_percent=Decimal("50"),
            logistics_cost=Decimal("100"),
        )
        PriceRule.objects.filter(variant=variant).update(
            min_margin_percent=Decimal("60"),
        )
        variant.refresh_from_db()   # ← сбросить кэш price_rule
        assert min_price(variant, "wb") == Decimal("0")


# --- calculate_margin ---

@pytest.mark.django_db
class TestCalculateMargin:
    def test_basic(self, variant, price_rule, recipe, material_batch, workspace):
        # cost=75.57, price=200, commission=0, logistics=0, tax=8
        # margin = 200 - 75.57 - 0 - 0 - 8 = 116.43
        m = calculate_margin(variant, Decimal("200"), "wb")
        assert m == Decimal("116.43")

    def test_with_fee(self, variant, price_rule, recipe, material_batch, workspace):
        MarketplaceFee.objects.create(
            marketplace="wb", commission_percent=Decimal("20"),
            logistics_cost=Decimal("50"),
        )
        # cost=75.57, price=300, commission=60, logistics=50, tax=12
        # margin = 300 - 75.57 - 60 - 50 - 12 = 102.43
        m = calculate_margin(variant, Decimal("300"), "wb")
        assert m == Decimal("102.43")

    def test_margin_percent(self, variant, price_rule, recipe, material_batch, workspace):
        # margin=116.43, price=200 → 58.215% → 58.22
        pct = calculate_margin_percent(variant, Decimal("200"), "wb")
        assert pct == Decimal("58.22")


# --- profit_per_production_hour ---

@pytest.mark.django_db
class TestProfitPerProductionHour:
    def test_basic(self, variant, price_rule, recipe, material_batch, workspace):
        # margin=116.43, hours=45/60=0.75 → 116.43/0.75 = 155.24
        p = profit_per_production_hour(variant, Decimal("200"), "wb")
        assert p == Decimal("155.24")

    def test_no_profile(self, variant, recipe):
        variant.recipe.profile = None
        variant.recipe.save()
        assert profit_per_production_hour(variant, Decimal("200"), "wb") == Decimal("0")