from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class Movement:

    transaction_id: str

    timestamp: datetime

    category: str

    type: str

    asset_class: Optional[str]

    name: Optional[str]

    symbol: Optional[str]

    shares: Decimal

    price: Decimal

    amount: Decimal

    fee: Decimal

    tax: Decimal

    currency: str

    description: str