# core/apps/catalog/tests.py
import uuid

import pytest
from django.db import IntegrityError

from apps.catalog.models import Category, Product, ProductVariant, PlatformListing
from apps.guide.models import Color


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def category_root(db, workspace_id):
    return Category.objects.create(workspace_id=workspace_id, name="Для дома")


@pytest.fixture
def category_child(db, category_root):
    return Category.objects.create(
        workspace_id=category_root.workspace_id,
        parent=category_root, name="Органайзеры",
    )


@pytest.fixture
def product(db, workspace_id, category_child):
    return Product.objects.create(
        workspace_id=workspace_id, category=category_child, name="Органайзер",
    )


@pytest.fixture
def variant(db, product):
    return ProductVariant.objects.create(product=product, name="Зелёный")


# --- Category ---

@pytest.mark.django_db
class TestCategory:
    def test_str(self, category_root):
        assert str(category_root) == "Для дома"

    def test_root_path_and_depth(self, category_root):
        assert category_root.depth == 0
        assert category_root.path == f"{category_root.pk}/"
        
    def test_unique_root_name(self, workspace_id, category_root):
        with pytest.raises(IntegrityError):
            Category.objects.create(workspace_id=workspace_id, name="Для дома")

    def test_child_path_and_depth(self, category_root, category_child):
        assert category_child.depth == 1
        assert category_child.path == f"{category_root.pk}/{category_child.pk}/"

    def test_grandchild_path(self, category_child):
        grandchild = Category.objects.create(
            workspace_id=category_child.workspace_id,
            parent=category_child, name="Мелкие",
        )
        assert grandchild.depth == 2
        assert grandchild.path == (
            f"{category_child.parent.pk}/{category_child.pk}/{grandchild.pk}/"
        )

    def test_descendants(self, category_root, category_child):
        grandchild = Category.objects.create(
            workspace_id=category_root.workspace_id,
            parent=category_child, name="Мелкие",
        )
        ids = set(category_root.descendants().values_list("id", flat=True))
        assert ids == {category_root.id, category_child.id, grandchild.id}

    def test_unique_name_per_parent(self, workspace_id, category_root, category_child,):
        with pytest.raises(IntegrityError):
            Category.objects.create(
                workspace_id=workspace_id, 
                parent=category_root, 
                name="Органайзеры",
            )

    def test_same_name_different_parent(self, workspace_id, category_root):
        c = Category.objects.create(
            workspace_id=workspace_id, name="Органайзеры",
        )
        assert c.pk != category_root.pk


# --- Product ---

@pytest.mark.django_db
class TestProduct:
    def test_str(self, product):
        assert str(product) == "Органайзер"

    def test_unique_name_per_workspace(self, workspace_id, product):
        with pytest.raises(IntegrityError):
            Product.objects.create(workspace_id=workspace_id, name="Органайзер")

    def test_category_optional(self, workspace_id):
        p = Product.objects.create(workspace_id=workspace_id, name="Без категории")
        assert p.category is None


# --- ProductVariant ---

@pytest.mark.django_db
class TestProductVariant:
    def test_str(self, variant):
        assert str(variant) == "Органайзер / Зелёный"

    def test_unique_name_per_product(self, product, variant):
        with pytest.raises(IntegrityError):
            ProductVariant.objects.create(product=product, name="Зелёный")

    def test_color_optional(self, product):
        v = ProductVariant.objects.create(product=product, name="Красный")
        assert v.color is None

    def test_color_set(self, product):
        color = Color.objects.create(name="Зелёный", ral_code="6018")
        v = ProductVariant.objects.create(product=product, name="Зелёный", color=color)
        assert v.color.ral_code == "6018"


# --- PlatformListing ---

@pytest.mark.django_db
class TestPlatformListing:
    def test_str(self, variant):
        listing = PlatformListing.objects.create(
            variant=variant, marketplace="wb", platform_sku="WB-123",
        )
        assert str(listing) == "Органайзер / Зелёный @ Wildberries"

    def test_unique_variant_marketplace(self, variant):
        PlatformListing.objects.create(variant=variant, marketplace="wb")
        with pytest.raises(IntegrityError):
            PlatformListing.objects.create(variant=variant, marketplace="wb")

    def test_same_variant_different_marketplace(self, variant):
        PlatformListing.objects.create(variant=variant, marketplace="wb")
        l2 = PlatformListing.objects.create(variant=variant, marketplace="ozon")
        assert l2.pk is not None

    def test_default_status(self, variant):
        listing = PlatformListing.objects.create(variant=variant, marketplace="wb")
        assert listing.status == PlatformListing.Status.DRAFT