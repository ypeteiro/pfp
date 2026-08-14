from decimal import Decimal

import pytest

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


def test_portfolio_invested_matches_position_cost_basis():
    portfolio = Portfolio(
        positions={
            "VWCE": Position(
                symbol="VWCE",
                name="Vanguard FTSE All-World",
                shares=Decimal("2"),
                invested=Decimal("200"),
                average_price=Decimal("100"),
            ),
            "EUNL": Position(
                symbol="EUNL",
                name="iShares Core MSCI World",
                shares=Decimal("3"),
                invested=Decimal("300"),
                average_price=Decimal("100"),
            ),
        },
        invested=Decimal("500"),
    )

    assert portfolio.invested == sum(
        (position.invested for position in portfolio.positions.values()),
        Decimal("0"),
    )


def test_portfolio_rejects_inconsistent_invested_total():
    with pytest.raises(ValueError, match="Portfolio invested amount must equal position cost basis"):
        Portfolio(
            positions={
                "VWCE": Position(
                    symbol="VWCE",
                    name="Vanguard FTSE All-World",
                    shares=Decimal("2"),
                    invested=Decimal("200"),
                    average_price=Decimal("100"),
                )
            },
            invested=Decimal("250"),
        )
