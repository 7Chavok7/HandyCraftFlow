# core/apps/pricing/tests.py
import uuid
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Product, ProductVariant
from apps.pricing.models import PriceRule, PriceHistory


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def variant(db, workspace_id):
    product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
    return ProductVariant.objects.create(product=product, name="Зелёный")


# --- PriceRule ---

@pytest.mark.django_db
class TestPriceRule:
    def test_str(self, variant):
        rule = PriceRule.objects.create(
            variant=variant, min_margin_percent=Decimal("15"),
            target_margin_percent=Decimal("35"),
        )
        assert "15" in str(rule)
        assert "35" in str(rule)

    def test_default_strategy(self, variant):
        rule = PriceRule.objects.create(variant=variant)
        assert rule.strategy == PriceRule.Strategy.MIN_PRICE_GUARD

    def test_default_margins(self, variant):
        rule = PriceRule.objects.create(variant=variant)
        assert rule.min_margin_percent == Decimal("0")
        assert rule.target_margin_percent == Decimal("30")

    def test_one_to_one_variant(self, variant):
        PriceRule.objects.create(variant=variant)
        with pytest.raises(IntegrityError):
            PriceRule.objects.create(variant=variant)

    def test_fixed_price_optional(self, variant):
        rule = PriceRule.objects.create(variant=variant)
        assert rule.fixed_price is None

    def test_fixed_price_set(self, variant):
        rule = PriceRule.objects.create(
            variant=variant, strategy=PriceRule.Strategy.FIXED,
            fixed_price=Decimal("990.00"),
        )
        assert rule.fixed_price == Decimal("990.00")


# --- PriceHistory ---

@pytest.mark.django_db
class TestPriceHistory:
    def test_str(self, variant):
        h = PriceHistory.objects.create(
            variant=variant, price=Decimal("990.00"),
        )
        assert "990" in str(h)
        assert "Вручную" in str(h)

    def test_default_source(self, variant):
        h = PriceHistory.objects.create(variant=variant, price=Decimal("500"))
        assert h.source == PriceHistory.Source.MANUAL

    def test_multiple_entries_per_variant(self, variant):
        PriceHistory.objects.create(variant=variant, price=Decimal("500"))
        PriceHistory.objects.create(variant=variant, price=Decimal("600"))
        assert variant.price_history.count() == 2

    def test_ordering_newest_first(self, variant):
        h1 = PriceHistory.objects.create(variant=variant, price=Decimal("500"))
        h2 = PriceHistory.objects.create(variant=variant, price=Decimal("600"))
        entries = list(variant.price_history.all())
        assert entries[0] == h2
        assert entries[1] == h1