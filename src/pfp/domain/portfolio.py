from dataclasses import dataclass, field
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.investment import Investment
from pfp.domain.movement import Movement
from pfp.domain.position import Position
from pfp.domain.sale import Sale


@dataclass(slots=True)
class Portfolio:

    movements: list[Movement] = field(default_factory=list)
    accounts: list[Account] = field(default_factory=list)
    positions: dict[str, Position] = field(default_factory=dict)
    account_positions: dict[str, dict[str, Position]] = field(default_factory=dict)
    cash: Decimal = Decimal("0")
    invested: Decimal = Decimal("0")
    realized_gain_loss: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.invested < 0:
            raise ValueError("Invested amount cannot be negative")

        position_cost_basis = Decimal("0")
        for symbol, position in self.positions.items():
            if symbol != position.symbol:
                raise ValueError("Position key must match position symbol")
            if position.shares < 0:
                raise ValueError("Position shares cannot be negative")
            if position.invested < 0:
                raise ValueError("Position invested amount cannot be negative")
            if position.average_price < 0:
                raise ValueError("Position average price cannot be negative")
            position_cost_basis += position.invested

        if self.invested != position_cost_basis:
            raise ValueError("Portfolio invested amount must equal position cost basis")

        for account_id, positions in self.account_positions.items():
            for symbol, position in positions.items():
                if symbol != position.symbol:
                    raise ValueError("Account position key must match position symbol")
                position.validate()

    @property
    def market_value(self) -> Decimal | None:
        total = Decimal("0")
        for position in self.positions.values():
            if position.market_value is None:
                return None
            total += position.market_value
        return total

    @property
    def total_value(self) -> Decimal | None:
        market_value = self.market_value
        if market_value is None:
            return None
        return self.cash + market_value

    @property
    def unrealized_gain_loss(self) -> Decimal | None:
        market_value = self.market_value
        if market_value is None:
            return None
        return market_value - self.invested

    def add_capital_flow(self, flow: CapitalFlow) -> None:
        if flow.flow_type == FlowType.CONTRIBUTION:
            self.cash += flow.amount
        elif flow.flow_type == FlowType.WITHDRAWAL:
            if flow.amount > self.cash:
                raise ValueError("Withdrawal exceeds portfolio cash")
            self.cash -= flow.amount
        else:
            raise ValueError(f"Unsupported capital flow type: {flow.flow_type}")
        self.validate()

    def add_investment(self, investment: Investment) -> None:
        if investment.amount > self.cash:
            raise ValueError("Investment exceeds portfolio cash")
        self.cash -= investment.amount
        self.invested += investment.amount
        position = self.positions.get(investment.symbol)
        if position is None:
            position = Position(investment.symbol, investment.symbol, investment.shares, investment.amount, investment.price, investment.portfolio_class)
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
