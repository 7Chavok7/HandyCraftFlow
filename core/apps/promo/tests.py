import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import Product, ProductVariant
from apps.promo.models import Promotion, PromotionItem


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def variant(db, workspace_id):
    product = Product.objects.create(workspace_id=workspace_id, name="Органайзер")
    return ProductVariant.objects.create(product=product, name="Зелёный")


@pytest.fixture
def promotion(db, workspace_id):
    now = datetime.now(timezone.utc)
    return Promotion.objects.create(
        workspace_id=workspace_id, marketplace="wb",
        name="Чёрная пятница", starts_at=now,
        ends_at=now + timedelta(days=7),
        discount_percent=Decimal("20"),
    )


# --- Promotion ---

@pytest.mark.django_db
class TestPromotion:
    def test_str(self, promotion):
        assert "Чёрная пятница" in str(promotion)
        assert "Wildberries" in str(promotion)

    def test_default_discount_zero(self, workspace_id):
        now = datetime.now(timezone.utc)
        p = Promotion.objects.create(
            workspace_id=workspace_id, marketplace="ozon", name="X",
            starts_at=now, ends_at=now + timedelta(days=1),
        )
        assert p.discount_percent == Decimal("0")

    def test_default_raw_payload_empty(self, promotion):
        assert promotion.raw_payload == {}

    def test_unique_external_id(self, workspace_id):
        now = datetime.now(timezone.utc)
        Promotion.objects.create(
            workspace_id=workspace_id, marketplace="wb", external_id="123",
            name="A", starts_at=now, ends_at=now + timedelta(days=1),
        )
        with pytest.raises(IntegrityError):
            Promotion.objects.create(
                workspace_id=workspace_id, marketplace="wb", external_id="123",
                name="B", starts_at=now, ends_at=now + timedelta(days=1),
            )

    def test_empty_external_id_does_not_conflict(self, workspace_id):
        now = datetime.now(timezone.utc)
        Promotion.objects.create(
            workspace_id=workspace_id, marketplace="wb", external_id="",
            name="A", starts_at=now, ends_at=now + timedelta(days=1),
        )
        p2 = Promotion.objects.create(
            workspace_id=workspace_id, marketplace="wb", external_id="",
            name="B", starts_at=now, ends_at=now + timedelta(days=1),
        )
        assert p2.pk is not None


# --- PromotionItem ---

@pytest.mark.django_db
class TestPromotionItem:
    def test_str(self, promotion, variant):
        item = PromotionItem.objects.create(
            promotion=promotion, variant=variant,
            proposed_price=Decimal("799.00"),
        )
        assert "Чёрная пятница" in str(item)
        assert "Не решено" in str(item)

    def test_default_decision_pending(self, promotion, variant):
        item = PromotionItem.objects.create(
            promotion=promotion, variant=variant,
            proposed_price=Decimal("799"),
        )
        assert item.decision == PromotionItem.Decision.PENDING

    def test_unique_variant_per_promotion(self, promotion, variant):
        PromotionItem.objects.create(
            promotion=promotion, variant=variant,
            proposed_price=Decimal("799"),
        )
        with pytest.raises(IntegrityError):
            PromotionItem.objects.create(
                promotion=promotion, variant=variant,
                proposed_price=Decimal("899"),
            )

    def test_margin_fields_optional(self, promotion, variant):
        item = PromotionItem.objects.create(
            promotion=promotion, variant=variant,
            proposed_price=Decimal("799"),
        )
        assert item.margin_at_proposed is None
        assert item.snapshot_cost is None
        assert item.decided_at is None

    def test_decision_accepted(self, promotion, variant):
        item = PromotionItem.objects.create(
            promotion=promotion, variant=variant,
            proposed_price=Decimal("799"),
            decision=PromotionItem.Decision.ACCEPTED,
        )
        assert item.decision == "accepted"