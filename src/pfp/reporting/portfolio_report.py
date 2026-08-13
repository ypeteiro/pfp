from dataclasses import dataclass
from decimal import Decimal

from pfp.domain.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class PositionReport:
    symbol: str
    name: str
    portfolio_class: str | None
    shares: Decimal
    invested: Decimal
    market_price: Decimal | None
    market_value: Decimal | None
    gain_loss: Decimal | None


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

    @classmethod
    def from_portfolio(cls, portfolio: Portfolio) -> "PortfolioReport":
        positions = tuple(
            PositionReport(
                symbol=position.symbol,
                name=position.name,
                portfolio_class=position.portfolio_class,
                shares=position.shares,
                invested=position.invested,
                market_price=position.market_price,
                market_value=position.market_value,
                gain_loss=position.gain_loss,
            )
            for position in sorted(portfolio.positions.values(), key=lambda item: item.symbol)
        )

        market_value = sum(
            (position.market_value or Decimal("0") for position in portfolio.positions.values()),
            Decimal("0"),
        )
        unrealized_gain_loss = sum(
            (position.gain_loss or Decimal("0") for position in portfolio.positions.values()),
            Decimal("0"),
        )

        class_values = {
            "RV": Decimal("0"),
            "RF": Decimal("0"),
            "GOLD": Decimal("0"),
            "CRYPTO": Decimal("0"),
        }
        for position in portfolio.positions.values():
            if position.market_value is not None and position.portfolio_class in class_values:
                class_values[position.portfolio_class] += position.market_value

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
        )
