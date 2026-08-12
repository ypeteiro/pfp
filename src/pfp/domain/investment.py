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
