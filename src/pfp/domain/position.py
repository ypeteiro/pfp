from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Position:
    symbol: str
    name: str
    shares: Decimal = Decimal("0")
    invested: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    portfolio_class: str | None = None
    market_price: Decimal | None = None

    @property
    def market_value(self) -> Decimal | None:

        if self.market_price is None:
            return None

        return self.shares * self.market_price

    @property
    def gain_loss(self) -> Decimal | None:

        market_value = self.market_value

        if market_value is None:
            return None

        return market_value - self.invested