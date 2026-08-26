"""Abstractions for historical asset prices."""

from datetime import datetime
from decimal import Decimal
from typing import Protocol


class HistoricalPriceProvider(Protocol):
    def price(self, symbol: str, at: datetime) -> Decimal | None:
        """Return the price for an asset at a given datetime, if available."""


class MappingHistoricalPriceProvider:
    """Deterministic historical price provider backed by an in-memory mapping."""

    def __init__(self, prices: dict[datetime, dict[str, Decimal]]) -> None:
        self._prices = prices

    def price(self, symbol: str, at: datetime) -> Decimal | None:
        return self._prices.get(at, {}).get(symbol)
