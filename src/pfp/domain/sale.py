from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Sale:
    datetime: datetime
    symbol: str
    shares: Decimal
    amount: Decimal
    price: Decimal
    broker: str = "Trade Republic"
    operation_id: str | None = None
    account_id: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Sale symbol cannot be empty")
        if self.shares <= 0:
            raise ValueError("Sale shares must be positive")
        if self.amount <= 0:
            raise ValueError("Sale amount must be positive")
        if self.price <= 0:
            raise ValueError("Sale price must be positive")
        if not self.broker.strip():
            raise ValueError("Sale broker cannot be empty")
        if self.operation_id is not None and not self.operation_id.strip():
            raise ValueError("Sale operation_id cannot be empty")
        if self.account_id is not None and not self.account_id.strip():
            raise ValueError("Sale account_id cannot be empty")
