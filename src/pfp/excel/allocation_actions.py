"""Portfolio allocation guidance for the Excel export."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AllocationRow:
    asset_class: str
    target: Decimal
    current_value: Decimal
    current_weight: Decimal
    deviation: Decimal
    action: str


def build_allocation_rows(
    values: dict[str, Decimal],
    targets: dict[str, Decimal],
    total: Decimal,
    threshold: Decimal = Decimal("0.02"),
) -> tuple[AllocationRow, ...]:
    rows: list[AllocationRow] = []
    for asset_class, target in targets.items():
        value = values.get(asset_class, Decimal("0"))
        current_weight = value / total if total else Decimal("0")
        deviation = current_weight - target
        if deviation < -threshold:
            action = "Aumentar"
        elif deviation > threshold:
            action = "Reducir"
        else:
            action = "Mantener"
        rows.append(AllocationRow(asset_class, target, value, current_weight, deviation, action))
    return tuple(rows)
