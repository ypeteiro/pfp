from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.engine.portfolio_engine import PortfolioEngine


def test_external_cash_increases_account_and_consolidated_cash():
    movement = ExternalCashMovement(
        datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
        account_id="ABANCA_AHORRO",
        amount=Decimal("200"),
    )

    portfolio = PortfolioEngine().build(
        [],
        opening_balances=[AccountOpeningBalance("ABANCA_AHORRO", date(2026, 1, 1), Decimal("1000"))],
        external_cash_movements=[movement],
    )

    account = portfolio.accounts[0]
    assert account.balance == Decimal("1200")
    assert portfolio.cash == Decimal("1200")


def test_external_cash_outflow_decreases_account_and_consolidated_cash():
    movement = ExternalCashMovement(
        datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
        account_id="ABANCA_AHORRO",
        amount=Decimal("-200"),
    )

    portfolio = PortfolioEngine().build(
        [],
        opening_balances=[AccountOpeningBalance("ABANCA_AHORRO", date(2026, 1, 1), Decimal("1000"))],
        external_cash_movements=[movement],
    )

    assert portfolio.accounts[0].balance == Decimal("800")
    assert portfolio.cash == Decimal("800")


def test_external_cash_movement_currency_must_match_account():
    movement = ExternalCashMovement(
        datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
        account_id="ABANCA_AHORRO",
        amount=Decimal("200"),
        currency="USD",
    )

    with pytest.raises(ValueError, match="External cash movement currency does not match account currency"):
        PortfolioEngine().build(
            [],
            opening_balances=[AccountOpeningBalance("ABANCA_AHORRO", date(2026, 1, 1), Decimal("1000"), currency="EUR")],
            external_cash_movements=[movement],
        )


def test_external_cash_movement_can_create_account_without_opening_balance():
    movement = ExternalCashMovement(
        datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
        account_id="ABANCA_AHORRO",
        amount=Decimal("200"),
    )

    portfolio = PortfolioEngine().build([], external_cash_movements=[movement])

    assert portfolio.accounts[0].account_id == "ABANCA_AHORRO"
    assert portfolio.accounts[0].balance == Decimal("200")
