from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.account_transfer import AccountTransfer
from pfp.engine.portfolio_engine import PortfolioEngine


def _transfer(source, destination, amount, currency="EUR"):
    return AccountTransfer(
        datetime=datetime(2026, 1, 2, tzinfo=timezone.utc),
        source_account=source,
        destination_account=destination,
        amount=Decimal(amount),
        currency=currency,
    )


def test_opening_balance_and_internal_transfer_preserve_consolidated_cash():
    portfolio = PortfolioEngine().build(
        [],
        opening_balances=[
            AccountOpeningBalance("ABANCA", date(2026, 1, 1), Decimal("25000")),
            AccountOpeningBalance("TR", date(2026, 1, 1), Decimal("0")),
        ],
        account_transfers=[_transfer("ABANCA", "TR", "800")],
    )

    balances = {account.account_id: account.balance for account in portfolio.accounts}

    assert balances == {"ABANCA": Decimal("24200"), "TR": Decimal("800")}
    assert portfolio.cash == Decimal("25000")


def test_transfer_cannot_create_cash_from_insufficient_source_account():
    with pytest.raises(ValueError, match="Transfer exceeds source account cash"):
        PortfolioEngine().build(
            [],
            opening_balances=[
                AccountOpeningBalance("ABANCA", date(2026, 1, 1), Decimal("500")),
                AccountOpeningBalance("TR", date(2026, 1, 1), Decimal("0")),
            ],
            account_transfers=[_transfer("ABANCA", "TR", "600")],
        )


def test_transfer_currency_must_match_both_account_currencies():
    with pytest.raises(ValueError, match="Transfer currency does not match source account currency"):
        PortfolioEngine().build(
            [],
            opening_balances=[
                AccountOpeningBalance("ABANCA", date(2026, 1, 1), Decimal("500"), currency="EUR"),
                AccountOpeningBalance("TR", date(2026, 1, 1), Decimal("0"), currency="EUR"),
            ],
            account_transfers=[_transfer("ABANCA", "TR", "100", currency="USD")],
        )
