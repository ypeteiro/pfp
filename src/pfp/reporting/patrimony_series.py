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
    market_value: Decimal = Decimal("0")


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
                market_value=snapshot.market_value,
            )
            for snapshot in snapshots
        )
