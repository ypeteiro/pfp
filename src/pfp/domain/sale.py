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
