"""Presentation-ready historical patrimony series."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_history import PatrimonyHistory, PatrimonySnapshot


@dataclass(frozen=True, slots=True)
class PatrimonyPoint:
    datetime: datetime
    patrimony: Decimal
    cumulative_contributed: Decimal
    investment_gain: Decimal


class PatrimonySeries:
    """Historical values reduced to the data required by charts and reports."""

    @classmethod
    def build(cls, snapshots: tuple[PatrimonySnapshot, ...]) -> tuple[PatrimonyPoint, ...]:
        return tuple(
            PatrimonyPoint(
                snapshot.datetime,
                snapshot.patrimony,
                snapshot.cumulative_contributed,
                snapshot.investment_gain,
            )
            for snapshot in snapshots
        )

    @classmethod
    def from_history(cls, history: PatrimonyHistory) -> tuple[PatrimonyPoint, ...]:
        """Build a presentation series from a precomputed history."""
        return cls.build(history)
