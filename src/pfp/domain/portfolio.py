from dataclasses import dataclass, field
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.movement import Movement
from pfp.domain.position import Position


@dataclass(slots=True)
class Portfolio:

    movements: list[Movement] = field(default_factory=list)

    accounts: list[Account] = field(default_factory=list)

    positions: dict[str, Position] = field(default_factory=dict)

    cash: Decimal = Decimal("0")

    invested: Decimal = Decimal("0")

    realized_gain_loss: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.invested < 0:
            raise ValueError("Invested amount cannot be negative")

        for symbol, position in self.positions.items():
            if symbol != position.symbol:
                raise ValueError("Position key must match position symbol")
            if position.shares < 0:
                raise ValueError("Position shares cannot be negative")
            if position.invested < 0:
                raise ValueError("Position invested amount cannot be negative")
            if position.average_price < 0:
                raise ValueError("Position average price cannot be negative")
