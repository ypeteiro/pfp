from datetime import date
from decimal import Decimal

import pytest

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.engine.portfolio_engine import PortfolioEngine


def test_account_opening_balance_validates_account_and_currency():
    opening = AccountOpeningBalance(
        account_id="ABANCA",
        date=date(2026, 8, 19),
        amount=Decimal("31106"),
    )
    assert opening.account_id == "ABANCA"
    assert opening.amount == Decimal("31106")
    assert opening.currency == "EUR"


def test_account_opening_balance_rejects_negative_amount():
    with pytest.raises(ValueError, match="Opening balance cannot be negative"):
        AccountOpeningBalance(
            account_id="ABANCA",
            date=date(2026, 8, 19),
            amount=Decimal("-1"),
        )


def test_build_uses_account_opening_balance_as_initial_cash():
    opening = AccountOpeningBalance(
        account_id="ABANCA",
        date=date(2026, 8, 19),
        amount=Decimal("31106"),
    )

    portfolio = PortfolioEngine().build([], opening_balances=[opening])

    assert portfolio.cash == Decimal("31106")
    assert len(portfolio.accounts) == 1
    assert portfolio.accounts[0].name == "ABANCA"
    assert portfolio.accounts[0].broker == "ABANCA"
    assert portfolio.accounts[0].balance == Decimal("31106")
    assert portfolio.positions == {}


def test_build_adds_movements_to_account_opening_balance():
    from datetime import datetime, timezone

    from pfp.domain.movement import Movement

    opening = AccountOpeningBalance(
        account_id="ABANCA",
        date=date(2026, 8, 19),
        amount=Decimal("31106"),
    )
    movement = Movement(
        datetime=datetime(2026, 8, 20, tzinfo=timezone.utc),
        date=date(2026, 8, 20),
        account_type="BANK",
        account_id="ABANCA",
        broker="ABANCA",
        category="CASH",
        type="TRANSFER_INBOUND",
        asset_class=None,
        name=None,
        symbol=None,
        shares=None,
        price=None,
        amount=Decimal("500"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description="Subsequent movement",
        transaction_id="opening-balance-follow-up",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )

    portfolio = PortfolioEngine().build([movement], opening_balances=[opening])

    assert portfolio.cash == Decimal("31606")
    assert portfolio.accounts[0].balance == Decimal("31606")
