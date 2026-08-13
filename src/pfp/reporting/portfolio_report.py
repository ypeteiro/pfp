from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class PositionReport:
    symbol: str
    name: str
    portfolio_class: str | None
    shares: Decimal
    invested: Decimal
    average_price: Decimal
    market_price: Decimal | None
    market_value: Decimal | None
    weight: Decimal | None
    gain_loss: Decimal | None


@dataclass(frozen=True, slots=True)
class AccountReport:
    name: str
    broker: str
    currency: str
    balance: Decimal


@dataclass(frozen=True, slots=True)
class MovementReport:
    datetime: datetime
    broker: str
    category: str
    type: str
    asset_class: str | None
    symbol: str | None
    name: str | None
    shares: Decimal | None
    price: Decimal | None
    amount: Decimal
    fee: Decimal
    tax: Decimal
    currency: str
    description: str | None
    transaction_id: str


@dataclass(frozen=True, slots=True)
class PortfolioReport:
    cash: Decimal
    invested: Decimal
    market_value: Decimal
    total_value: Decimal
    realized_gain_loss: Decimal
    unrealized_gain_loss: Decimal
    equity_value: Decimal
    fixed_income_value: Decimal
    gold_value: Decimal
    crypto_value: Decimal
    positions: tuple[PositionReport, ...]
    accounts: tuple[AccountReport, ...] = ()
    movements: tuple[MovementReport, ...] = ()

    @classmethod
    def from_portfolio(cls, portfolio: Portfolio) -> "PortfolioReport":
        market_value = sum(
            (position.market_value or Decimal("0") for position in portfolio.positions.values()),
            Decimal("0"),
        )
        unrealized_gain_loss = sum(
            (position.gain_loss or Decimal("0") for position in portfolio.positions.values()),
            Decimal("0"),
        )

        class_values = {"RV": Decimal("0"), "RF": Decimal("0"), "GOLD": Decimal("0"), "CRYPTO": Decimal("0")}
        for position in portfolio.positions.values():
            if position.market_value is not None and position.portfolio_class in class_values:
                class_values[position.portfolio_class] += position.market_value

        positions = tuple(
            PositionReport(
                symbol=position.symbol,
                name=position.name,
                portfolio_class=position.portfolio_class,
                shares=position.shares,
                invested=position.invested,
                average_price=(
                    position.average_price
                    if position.average_price
                    else (position.invested / position.shares if position.shares else Decimal("0"))
                ),
                market_price=position.market_price,
                market_value=position.market_value,
                weight=(position.market_value / market_value if market_value else None),
                gain_loss=position.gain_loss,
            )
            for position in sorted(portfolio.positions.values(), key=lambda item: item.symbol)
        )

        accounts = tuple(
            AccountReport(account.name, account.broker, account.currency, account.balance)
            for account in sorted(portfolio.accounts, key=lambda item: (item.broker, item.name))
        )

        movements = tuple(
            MovementReport(
                datetime=movement.datetime,
                broker=movement.broker,
                category=movement.category,
                type=movement.type,
                asset_class=movement.asset_class,
                symbol=movement.symbol,
                name=movement.name,
                shares=movement.shares,
                price=movement.price,
                amount=movement.amount,
                fee=movement.fee,
                tax=movement.tax,
                currency=movement.currency,
                description=movement.description,
                transaction_id=movement.transaction_id,
            )
            for movement in sorted(portfolio.movements, key=lambda item: item.datetime)
        )

        return cls(
            cash=portfolio.cash,
            invested=portfolio.invested,
            market_value=market_value,
            total_value=portfolio.cash + market_value,
            realized_gain_loss=portfolio.realized_gain_loss,
            unrealized_gain_loss=unrealized_gain_loss,
            equity_value=class_values["RV"],
            fixed_income_value=class_values["RF"],
            gold_value=class_values["GOLD"],
            crypto_value=class_values["CRYPTO"],
            positions=positions,
            accounts=accounts,
            movements=movements,
        )
