from datetime import datetime, timezone
from decimal import Decimal

from pfp.engine.investment_engine import InvestmentEngine


def test_create_investment():
    investment = InvestmentEngine().create(
        symbol="IE00B4L5Y983",
        shares=Decimal("4"),
        amount=Decimal("500"),
        portfolio_class="EQUITY",
        datetime=datetime(
            2026,
            8,
            7,
            tzinfo=timezone.utc,
        ),
    )

    assert investment.symbol == "IE00B4L5Y983"
    assert investment.shares == Decimal("4")
    assert investment.amount == Decimal("500")
    assert investment.price == Decimal("125")
    assert investment.portfolio_class == "EQUITY"
    assert investment.broker == "Trade Republic"


def test_create_investment_calculates_price():
    investment = InvestmentEngine().create(
        symbol="GOLD",
        shares=Decimal("2.5"),
        amount=Decimal("250"),
        portfolio_class="GOLD",
        datetime=datetime.now(timezone.utc),
    )

    assert investment.price == Decimal("100")


def test_create_investment_rejects_zero_shares():
    try:
        InvestmentEngine().create(
            symbol="TEST",
            shares=Decimal("0"),
            amount=Decimal("100"),
            portfolio_class="EQUITY",
            datetime=datetime.now(timezone.utc),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Shares must be greater than zero"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_create_investment_rejects_zero_amount():
    try:
        InvestmentEngine().create(
            symbol="TEST",
            shares=Decimal("1"),
            amount=Decimal("0"),
            portfolio_class="EQUITY",
            datetime=datetime.now(timezone.utc),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Amount must be greater than zero"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_create_investment_rejects_empty_symbol():
    try:
        InvestmentEngine().create(
            symbol="",
            shares=Decimal("1"),
            amount=Decimal("100"),
            portfolio_class="EQUITY",
            datetime=datetime.now(timezone.utc),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Symbol must not be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )