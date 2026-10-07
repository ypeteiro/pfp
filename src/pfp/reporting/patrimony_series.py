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
    invested_cost: Decimal = Decimal("0")
    market_value: Decimal = Decimal("0")
    money_weighted_return: Decimal | None = None


class PatrimonySeries:
    """Historical values reduced to the data required by charts and reports."""

    @classmethod
    def build(cls, snapshots: tuple[PatrimonySnapshot, ...]) -> tuple[PatrimonyPoint, ...]:
        return tuple(
            PatrimonyPoint(
                datetime=snapshot.datetime,
                patrimony=snapshot.patrimony,
                cumulative_contributed=snapshot.cumulative_contributed,
                investment_gain=snapshot.investment_gain,
                invested_cost=snapshot.invested_cost,
                market_value=snapshot.market_value,
                money_weighted_return=snapshot.money_weighted_return,
            )
            for snapshot in snapshots
        )
