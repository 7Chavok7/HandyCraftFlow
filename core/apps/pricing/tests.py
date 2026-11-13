# core/apps/pricing/tests.py
import uuid
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Product, ProductVariant, Category
from apps.pricing.models import PriceRule, PriceHistory, MarketplaceFee


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
     
   
@pytest.mark.django_db
class TestMarketplaceFee:
    def test_str(self):
        fee = MarketplaceFee.objects.create(
            marketplace="wb", commission_percent=Decimal("20"),
            logistics_cost=Decimal("50"),
        )
        assert "Wildberries" in str(fee)
        assert "20" in str(fee)

    def test_str_with_category(self):
        cat = Category.objects.create(workspace_id=uuid.uuid4(), name="Декор")
        fee = MarketplaceFee.objects.create(
            marketplace="wb", category=cat,
            commission_percent=Decimal("25"),
        )
        assert "Декор" in str(fee)

    def test_unique_marketplace_category(self):
        MarketplaceFee.objects.create(marketplace="wb")
        with pytest.raises(IntegrityError):
            MarketplaceFee.objects.create(marketplace="wb")

    def test_same_marketplace_different_category(self):
        ws = uuid.uuid4()
        c1 = Category.objects.create(workspace_id=ws, name="Декор")
        c2 = Category.objects.create(workspace_id=ws, name="Кухня")
        MarketplaceFee.objects.create(marketplace="wb", category=c1)
        fee = MarketplaceFee.objects.create(marketplace="wb", category=c2)
        assert fee.pk is not None

    def test_defaults(self):
        fee = MarketplaceFee.objects.create(marketplace="ozon")
        assert fee.commission_percent == Decimal("0")
        assert fee.logistics_cost == Decimal("0")