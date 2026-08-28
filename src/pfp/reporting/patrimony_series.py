"""Presentation-ready historical patrimony series."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_history import PatrimonySnapshot


@dataclass(frozen=True, slots=True)
class PatrimonyPoint:
    datetime: datetime
    patrimony: Decimal
    cumulative_contributed: Decimal
    investment_gain: Decimal
    invested_cost: Decimal
    market_value: Decimal


class PatrimonySeries:
    """Historical values reduced to the data required by dashboard charts."""

    @classmethod
    def build(cls, snapshots: tuple[PatrimonySnapshot, ...]) -> tuple[PatrimonyPoint, ...]:
        return tuple(
            PatrimonyPoint(
                snapshot.datetime,
                snapshot.patrimony,
                snapshot.cumulative_contributed,
                snapshot.investment_gain,
                snapshot.invested_cost,
                snapshot.market_value,
            )
            for snapshot in snapshots
        )
