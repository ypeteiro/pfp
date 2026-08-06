from dataclasses import dataclass, field
from decimal import Decimal

from pfp.domain.movement import Movement
from pfp.domain.position import Position


@dataclass(slots=True)
class Portfolio:

    movements: list[Movement] = field(default_factory=list)

    positions: dict[str, Position] = field(default_factory=dict)

    cash: Decimal = Decimal("0")

    invested: Decimal = Decimal("0")