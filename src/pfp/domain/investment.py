from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Investment:
    datetime: datetime
    symbol: str
    shares: Decimal
    amount: Decimal
    price: Decimal
    portfolio_class: str
    broker: str = "Trade Republic"
    operation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Investment symbol cannot be empty")
        if self.shares <= 0:
            raise ValueError("Investment shares must be positive")
        if self.amount <= 0:
            raise ValueError("Investment amount must be positive")
        if self.price <= 0:
            raise ValueError("Investment price must be positive")
        if not self.portfolio_class.strip():
            raise ValueError("Investment portfolio_class cannot be empty")
        if not self.broker.strip():
            raise ValueError("Investment broker cannot be empty")
        if self.operation_id is not None and not self.operation_id.strip():
            raise ValueError("Investment operation_id cannot be empty")
