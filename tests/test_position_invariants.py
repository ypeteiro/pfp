from decimal import Decimal

import pytest

from pfp.domain.position import Position
from pfp.engine.portfolio_engine import PortfolioEngine


def test_zero_share_position_must_have_zero_cost_basis():
    with pytest.raises(ValueError, match="Zero-share position cannot have invested amount"):
        Position(
            symbol="TEST",
            name="Test",
            shares=Decimal("0"),
            invested=Decimal("100"),
            average_price=Decimal("0"),
        )


def test_zero_share_position_must_have_zero_average_price():
    with pytest.raises(ValueError, match="Zero-share position cannot have average price"):
        Position(
            symbol="TEST",
            name="Test",
            shares=Decimal("0"),
            invested=Decimal("0"),
            average_price=Decimal("100"),
        )


def test_position_average_price_must_match_cost_basis():
    with pytest.raises(ValueError, match="Average price must equal invested amount divided by shares"):
        Position(
            symbol="TEST",
            name="Test",
            shares=Decimal("2"),
            invested=Decimal("200"),
            average_price=Decimal("90"),
        )


def test_position_accepts_consistent_cost_basis():
    position = Position(
        symbol="TEST",
        name="Test",
        shares=Decimal("2"),
        invested=Decimal("200"),
        average_price=Decimal("100"),
    )
    position.validate()


def test_partial_sale_preserves_average_cost_basis_invariant():
    portfolio = PortfolioEngine().build(movements=[])
    portfolio.cash = Decimal("1000")
    PortfolioEngine()._apply_buy(
        portfolio,
        "TEST",
        "Test",
        Decimal("10"),
        Decimal("1000"),
        "RV",
    )
    PortfolioEngine()._apply_sell(portfolio, "TEST", Decimal("4"), Decimal("600"))

    position = portfolio.positions["TEST"]
    assert position.shares == Decimal("6")
    assert position.invested == Decimal("600")
    assert position.average_price == Decimal("100")
    position.validate()


def test_full_sale_leaves_zero_cost_basis():
    portfolio = PortfolioEngine().build(movements=[])
    portfolio.cash = Decimal("1000")
    PortfolioEngine()._apply_buy(
        portfolio,
        "TEST",
        "Test",
        Decimal("10"),
        Decimal("1000"),
        "RV",
    )
    PortfolioEngine()._apply_sell(portfolio, "TEST", Decimal("10"), Decimal("1200"))

    position = portfolio.positions["TEST"]
    assert position.shares == Decimal("0")
    assert position.invested == Decimal("0")
    assert position.average_price == Decimal("0")
    position.validate()
    assert portfolio.realized_gain_loss == Decimal("200")
