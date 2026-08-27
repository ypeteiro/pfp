from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.account_catalog import DEFAULT_ACCOUNT_CATALOG
from pfp.domain.asset_catalog import AssetCatalog
from pfp.domain.portfolio import Portfolio
from pfp.reporting.patrimony_series import PatrimonyPoint


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
    account_id: str | None = None
    invested: Decimal = Decimal("0")
    market_value: Decimal | None = Decimal("0")
    total_value: Decimal | None = Decimal("0")
    is_investable: bool = True


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
    price_consulted_at: datetime | None = None
    patrimony_series: tuple[PatrimonyPoint, ...] = ()

    @property
    def investable_cash(self) -> Decimal:
        return sum((account.balance for account in self.accounts if account.is_investable), Decimal("0"))

    @property
    def security_fund_cash(self) -> Decimal:
        return sum((account.balance for account in self.accounts if not account.is_investable), Decimal("0"))

    @classmethod
    def from_portfolio(cls, portfolio: Portfolio, price_consulted_at: datetime | None = None, patrimony_series: tuple[PatrimonyPoint, ...] = ()) -> "PortfolioReport":
        market_value = sum((position.market_value or Decimal("0") for position in portfolio.positions.values()), Decimal("0"))
        unrealized_gain_loss = sum((position.gain_loss or Decimal("0") for position in portfolio.positions.values()), Decimal("0"))
        class_map = {"RV": "RV", "EQUITY": "RV", "STOCK": "RV", "RF": "RF", "FIXED_INCOME": "RF", "GOLD": "GOLD", "CRYPTO": "CRYPTO"}
        class_values = {"RV": Decimal("0"), "RF": Decimal("0"), "GOLD": Decimal("0"), "CRYPTO": Decimal("0")}
        for position in portfolio.positions.values():
            normalized_class = class_map.get(position.portfolio_class)
            if position.market_value is not None and normalized_class is not None:
                class_values[normalized_class] += position.market_value

        positions = []
        for position in sorted(portfolio.positions.values(), key=lambda item: item.symbol):
            asset = AssetCatalog.get(position.symbol)
            market_price = position.market_price
            market_value_for_position = position.market_value
            gain_loss = position.gain_loss
            positions.append(PositionReport(
                symbol=position.symbol,
                name=asset.name if asset else position.name,
                portfolio_class=class_map.get(position.portfolio_class, position.portfolio_class),
                shares=position.shares,
                invested=position.invested,
                average_price=position.average_price or (position.invested / position.shares if position.shares else Decimal("0")),
                market_price=market_price,
                market_value=market_value_for_position,
                weight=(market_value_for_position / market_value if market_value and market_value_for_position is not None else None),
                gain_loss=gain_loss,
                isin=asset.isin if asset else (position.symbol if position.symbol.upper().startswith(("IE", "US")) else None),
                ticker=asset.ticker if asset else (position.symbol if not position.symbol.upper().startswith(("IE", "US")) else None),
            ))

        account_reports = []
        for account in sorted(portfolio.accounts, key=lambda item: (item.broker, item.name)):
            account_id = account.id
            account_positions = portfolio.account_positions.get(account_id, {})
            account_invested = sum((position.invested for position in account_positions.values()), Decimal("0"))
            account_market_value = Decimal("0")
            prices_complete = True
            for position in account_positions.values():
                if position.market_value is None:
                    prices_complete = False
                else:
                    account_market_value += position.market_value
            account_market_value_result = account_market_value if prices_complete else None
            account_total = account.balance + account_market_value if account_market_value_result is not None else None
            definition = DEFAULT_ACCOUNT_CATALOG.get(account_id) if DEFAULT_ACCOUNT_CATALOG.contains(account_id) else None
            account_reports.append(AccountReport(
                name=account.name,
                broker=account.broker,
                currency=account.currency,
                balance=account.balance,
                account_id=account_id,
                invested=account_invested,
                market_value=account_market_value_result,
                total_value=account_total,
                is_investable=definition.is_investable if definition is not None else True,
            ))
        accounts = tuple(account_reports)

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
            price_consulted_at=price_consulted_at,
            patrimony_series=patrimony_series,
        )
