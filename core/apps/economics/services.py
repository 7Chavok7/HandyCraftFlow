# core/apps/economics/services.py
from decimal import Decimal

from django.db.models import F, Sum

from apps.materials.models import MaterialType
from apps.pricing.models import MarketplaceFee, PriceRule
from apps.production.models import Recipe


def avg_material_cost(material_type: MaterialType) -> Decimal:
    """Средневзвешенная цена за единицу по доступным партиям."""
    agg = material_type.batches.filter(is_exhausted=False).aggregate(
        value=Sum(F("qty_remaining") * F("unit_cost")),
        qty=Sum("qty_remaining"),
    )
    if not agg["qty"]:
        return Decimal("0")
    return (agg["value"] / agg["qty"]).quantize(Decimal("0.0001"))


def calculate_cost(variant) -> Decimal:
    """Себестоимость единицы варианта.

    Σ(норма × (1 + waste%) × средняя цена материала)
    + время производства × ставка часа оборудования
    + труд × эффективная ставка часа
    + надбавка варианта
    """
    try:
        recipe = variant.recipe
    except Recipe.DoesNotExist:
        return variant.extra_cost or Decimal("0")

    total = Decimal("0")

    # материалы
    for line in recipe.lines.select_related("material_type"):
        price = avg_material_cost(line.material_type)
        waste_factor = Decimal("1") + (line.waste_percent / Decimal("100"))
        total += line.qty_per_unit * waste_factor * price

    # оборудование
    if recipe.profile and recipe.profile.expected_duration_min:
        ws_settings = _get_workspace_settings(variant)
        hours = Decimal(recipe.profile.expected_duration_min) / Decimal("60")
        total += hours * ws_settings.equipment_hour_cost

    # труд
    ws_settings = _get_workspace_settings(variant)
    hours_labor = Decimal(recipe.labor_minutes) / Decimal("60")
    total += hours_labor * ws_settings.effective_labor_rate

    # надбавка варианта
    total += variant.extra_cost or Decimal("0")

    return total.quantize(Decimal("0.01"))


def get_marketplace_fee(variant, marketplace: str) -> MarketplaceFee | None:
    """Комиссия по категории варианта, иначе общая ставка площадки."""
    category = variant.product.category
    if category:
        fee = MarketplaceFee.objects.filter(
            marketplace=marketplace, category=category,
        ).first()
        if fee:
            return fee
    return MarketplaceFee.objects.filter(
        marketplace=marketplace, category__isnull=True,
    ).first()


def calculate_margin(variant, price: Decimal, marketplace: str) -> Decimal:
    """Маржа в рублях: цена − себестоимость − комиссия − логистика − налог."""
    cost = calculate_cost(variant)
    fee = get_marketplace_fee(variant, marketplace)
    ws_settings = _get_workspace_settings(variant)

    commission = Decimal("0")
    logistics = Decimal("0")
    if fee:
        commission = price * fee.commission_percent / Decimal("100")
        logistics = fee.logistics_cost

    tax = price * ws_settings.tax_rate / Decimal("100")

    return (price - cost - commission - logistics - tax).quantize(Decimal("0.01"))


def calculate_margin_percent(variant, price: Decimal, marketplace: str) -> Decimal:
    """Маржа в процентах от цены."""
    if price == 0:
        return Decimal("0")
    margin = calculate_margin(variant, price, marketplace)
    return (margin / price * Decimal("100")).quantize(Decimal("0.01"))


def min_price(variant, marketplace: str) -> Decimal:
    """Красная линия: минимальная цена, при которой маржа >= min_margin_percent.

    price - cost - price*commission% - logistics - price*tax% = price * min_margin%
    price * (1 - commission% - tax% - min_margin%) = cost + logistics
    price = (cost + logistics) / (1 - commission% - tax% - min_margin%)
    """
    cost = calculate_cost(variant)
    fee = get_marketplace_fee(variant, marketplace)
    ws_settings = _get_workspace_settings(variant)

    try:
        rule = PriceRule.objects.get(variant=variant)   # ← из БД
    except PriceRule.DoesNotExist:
        rule = None

    min_margin = rule.min_margin_percent if rule else Decimal("0")
    commission = fee.commission_percent if fee else Decimal("0")
    logistics = fee.logistics_cost if fee else Decimal("0")

    denominator = (
        Decimal("1")
        - commission / Decimal("100")
        - ws_settings.tax_rate / Decimal("100")
        - min_margin / Decimal("100")
    )
    if denominator <= 0:
        return Decimal("0")  # защита от деления на ноль / невозможной маржи

    return ((cost + logistics) / denominator).quantize(Decimal("0.01"))


def profit_per_production_hour(variant, price: Decimal, marketplace: str) -> Decimal:
    """Доход с часа производства. Ключевая метрика 'что выгоднее печатать'."""
    try:
        recipe = variant.recipe
    except Recipe.DoesNotExist:
        return Decimal("0")

    if not recipe.profile or not recipe.profile.expected_duration_min:
        return Decimal("0")

    margin = calculate_margin(variant, price, marketplace)
    hours = Decimal(recipe.profile.expected_duration_min) / Decimal("60")
    return (margin / hours).quantize(Decimal("0.01"))


def _get_workspace_settings(variant):
    """Настройки workspace через variant → product → workspace_id."""
    from apps.workspaces.models import WorkspaceSettings
    return WorkspaceSettings.objects.get(workspace_id=variant.product.workspace_id)