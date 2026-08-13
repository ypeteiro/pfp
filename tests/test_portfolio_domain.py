from decimal import Decimal

import pytest

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


def test_portfolio_rejects_negative_invested():
    with pytest.raises(ValueError, match="Invested amount cannot be negative"):
        Portfolio(invested=Decimal("-1"))


def test_portfolio_rejects_position_key_mismatch():
    with pytest.raises(ValueError, match="Position key must match position symbol"):
        Portfolio(
            positions={
                "EUNL": Position(symbol="VWCE", name="World"),
            }
        )


def test_portfolio_accepts_zero_invested_and_closed_position():
    portfolio = Portfolio(
        positions={
            "EUNL": Position(
                symbol="EUNL",
                name="World",
                shares=Decimal("0"),
                invested=Decimal("0"),
                average_price=Decimal("0"),
            )
        }
    )

    portfolio.validate()


def test_portfolio_validate_detects_mutated_negative_position():
    portfolio = Portfolio()
    position = Position(symbol="EUNL", name="World")
    portfolio.positions["EUNL"] = position
    position.invested = Decimal("-1")

    with pytest.raises(ValueError, match="Position invested amount cannot be negative"):
        portfolio.validate()


def test_portfolio_validate_accepts_matching_positions():
    portfolio = Portfolio(
        invested=Decimal("1000"),
        positions={
            "EUNL": Position(
                symbol="EUNL",
                name="World",
                shares=Decimal("10"),
                invested=Decimal("1000"),
                average_price=Decimal("100"),
            )
        },
    )

    portfolio.validate()
