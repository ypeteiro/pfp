from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.asset_catalog import AssetCatalog
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
    isin: str | None = None
    ticker: str | None = None


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
        market_value = sum((position.market_value or Decimal("0") for position in portfolio.positions.values()), Decimal("0"))
        unrealized_gain_loss = sum((position.gain_loss or Decimal("0") for position in portfolio.positions.values()), Decimal("0"))
        class_map = {"RV": "RV", "EQUITY": "RV", "RF": "RF", "FIXED_INCOME": "RF", "GOLD": "GOLD", "CRYPTO": "CRYPTO"}
        class_values = {"RV": Decimal("0"), "RF": Decimal("0"), "GOLD": Decimal("0"), "CRYPTO": Decimal("0")}
        for position in portfolio.positions.values():
            normalized_class = class_map.get(position.portfolio_class)
            if position.market_value is not None and normalized_class is not None:
                class_values[normalized_class] += position.market_value

        positions = []
        for position in sorted(portfolio.positions.values(), key=lambda item: item.symbol):
            asset = AssetCatalog.get(position.symbol)
            market_price = position.market_price or (position.invested / position.shares if position.shares else None)
            market_value_for_position = position.market_value or (position.shares * market_price if market_price is not None else None)
            gain_loss = position.gain_loss if position.gain_loss is not None else (market_value_for_position - position.invested if market_value_for_position is not None else None)
            positions.append(PositionReport(
                symbol=position.symbol,
                name=asset.name if asset else position.name,
                portfolio_class=class_map.get(position.portfolio_class, position.portfolio_class),
                shares=position.shares,
                invested=position.invested,
                average_price=position.average_price or (position.invested / position.shares if position.shares else Decimal("0")),
                market_price=market_price,
                market_value=market_value_for_position,
                weight=(market_value_for_position / market_value if market_value else None),
                gain_loss=gain_loss,
                isin=asset.isin if asset else (position.symbol if position.symbol.upper().startswith("IE") else None),
                ticker=asset.ticker if asset else (position.symbol if not position.symbol.upper().startswith("IE") else None),
            ))

        accounts = tuple(AccountReport(a.name, a.broker, a.currency, a.balance) for a in sorted(portfolio.accounts, key=lambda item: (item.broker, item.name)))
        movements = tuple(MovementReport(m.datetime, m.broker, m.category, m.type, m.asset_class, m.symbol, m.name, m.shares, m.price, m.amount, m.fee, m.tax, m.currency, m.description, m.transaction_id) for m in sorted(portfolio.movements, key=lambda item: item.datetime))

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
            positions=tuple(positions),
            accounts=accounts,
            movements=movements,
        )
