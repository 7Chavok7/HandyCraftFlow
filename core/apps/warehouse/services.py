# core/apps/warehouse/services.py
from decimal import Decimal

from django.db import transaction

from apps.warehouse.models import Stock, StockLedger


@transaction.atomic
def adjust_stock(*, stock: Stock, new_qty: Decimal, comment: str = "") -> StockLedger | None:
    """Инвентаризация: установить фактический остаток."""
    diff = Decimal(new_qty) - stock.qty
    if diff == 0:
        return None

    stock.qty = Decimal(new_qty)
    stock.save(update_fields=["qty", "updated_at"])

    return StockLedger.objects.create(
        variant=stock.variant,
        warehouse=stock.warehouse,
        movement_type=StockLedger.MovementType.ADJUSTMENT,
        qty=diff,
        comment=comment or "Инвентаризация",
    )


@transaction.atomic
def reserve_stock(*, stock: Stock, qty: Decimal, comment: str = "") -> StockLedger:
    """Зарезервировать qty под заказ. Проверка: available_qty >= qty."""
    qty = Decimal(qty)
    if qty <= 0:
        raise ValueError("Количество резерва должно быть > 0")

    available = stock.available_qty
    if available < qty:
        raise ValueError(
            f"Недостаточно доступного остатка: {available}, требуется {qty}"
        )

    stock.reserved_qty += qty
    stock.save(update_fields=["reserved_qty", "updated_at"])

    return StockLedger.objects.create(
        variant=stock.variant,
        warehouse=stock.warehouse,
        movement_type=StockLedger.MovementType.RESERVE,
        qty=Decimal("0"),
        comment=comment or f"Резерв {qty}",
    )


@transaction.atomic
def unreserve_stock(*, stock: Stock, qty: Decimal, comment: str = "") -> StockLedger:
    """Снять резерв."""
    qty = Decimal(qty)
    if qty <= 0:
        raise ValueError("Количество снятия резерва должно быть > 0")

    if stock.reserved_qty < qty:
        raise ValueError(
            f"Недостаточно резерва: {stock.reserved_qty}, требуется {qty}"
        )

    stock.reserved_qty -= qty
    stock.save(update_fields=["reserved_qty", "updated_at"])

    return StockLedger.objects.create(
        variant=stock.variant,
        warehouse=stock.warehouse,
        movement_type=StockLedger.MovementType.UNRESERVE,
        qty=Decimal("0"),
        comment=comment or f"Снятие резерва {qty}",
    )