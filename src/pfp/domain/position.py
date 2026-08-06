from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Position:

    symbol: str

    name: str

    shares: Decimal = Decimal("0")

    invested: Decimal = Decimal("0")

    average_price: Decimal = Decimal("0")