from dataclasses import dataclass, field
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.capital_flow import CapitalFlow, CapitalFlowType
from pfp.domain.investment import Investment
from pfp.domain.movement import Movement
from pfp.domain.position import Position
from pfp.domain.sale import Sale


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

    def add_capital_flow(self, flow: CapitalFlow) -> None:
        if flow.type == CapitalFlowType.CONTRIBUTION:
            self.cash += flow.amount
        elif flow.type == CapitalFlowType.WITHDRAWAL:
            if flow.amount > self.cash:
                raise ValueError("Withdrawal exceeds portfolio cash")
            self.cash -= flow.amount
        else:
            raise ValueError(f"Unsupported capital flow type: {flow.type}")

        self.validate()

    def add_investment(self, investment: Investment) -> None:
        if investment.amount > self.cash:
            raise ValueError("Investment exceeds portfolio cash")

        self.cash -= investment.amount
        self.invested += investment.amount

        position = self.positions.get(investment.symbol)
        if position is None:
            position = Position(
                symbol=investment.symbol,
                name=investment.symbol,
                shares=investment.shares,
                invested=investment.amount,
                average_price=investment.price,
                portfolio_class=investment.portfolio_class,
            )
            self.positions[investment.symbol] = position
        else:
            position.shares += investment.shares
            position.invested += investment.amount
            position.average_price = position.invested / position.shares
            if position.portfolio_class is None:
                position.portfolio_class = investment.portfolio_class
            position.validate()

        self.validate()

    def add_sale(self, sale: Sale) -> None:
        position = self.positions.get(sale.symbol)
        if position is None:
            raise ValueError(f"Cannot sell unknown position: {sale.symbol}")
        if sale.shares > position.shares:
            raise ValueError("Sale shares exceed current position")

        cost_basis = position.average_price * sale.shares
        self.cash += sale.amount
        self.invested -= cost_basis
        self.realized_gain_loss += sale.amount - cost_basis

        position.shares -= sale.shares
        position.invested -= cost_basis

        if position.shares == 0:
            position.invested = Decimal("0")
            position.average_price = Decimal("0")
        else:
            position.average_price = position.invested / position.shares

        position.validate()
        self.validate()
