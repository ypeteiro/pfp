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

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Position symbol cannot be empty")
        if not self.name.strip():
            raise ValueError("Position name cannot be empty")
        if self.shares < 0:
            raise ValueError("Shares cannot be negative")
        if self.invested < 0:
            raise ValueError("Invested amount cannot be negative")
        if self.average_price < 0:
            raise ValueError("Average price cannot be negative")

        if self.shares == 0:
            if self.invested != 0:
                raise ValueError("Zero-share position cannot have invested amount")
            if self.average_price != 0:
                raise ValueError("Zero-share position cannot have average price")
        else:
            expected_average = self.invested / self.shares
            if self.average_price != expected_average:
                raise ValueError("Average price must equal invested amount divided by shares")

        if self.market_price is not None and self.market_price < 0:
            raise ValueError("Market price cannot be negative")

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
