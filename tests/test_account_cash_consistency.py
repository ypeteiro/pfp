from datetime import date
from decimal import Decimal

import pytest

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.account_transfer import AccountTransfer
from pfp.engine.portfolio_engine import PortfolioEngine


def test_opening_balance_and_internal_transfer_preserve_consolidated_cash():
    portfolio = PortfolioEngine().build(
        [],
        opening_balances=[
            AccountOpeningBalance("ABANCA", date(2026, 1, 1), Decimal("25000")),
            AccountOpeningBalance("TR", date(2026, 1, 1), Decimal("0")),
        ],
        account_transfers=[
            AccountTransfer(
                date=date(2026, 1, 2),
                source_account="ABANCA",
                destination_account="TR",
                amount=Decimal("800"),
                currency="EUR",
            )
        ],
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
            account_transfers=[
                AccountTransfer(
                    date=date(2026, 1, 2),
                    source_account="ABANCA",
                    destination_account="TR",
                    amount=Decimal("600"),
                    currency="EUR",
                )
            ],
        )


def test_transfer_currency_must_match_both_account_currencies():
    with pytest.raises(ValueError, match="Transfer currency does not match source account currency"):
        PortfolioEngine().build(
            [],
            opening_balances=[
                AccountOpeningBalance("ABANCA", date(2026, 1, 1), Decimal("500"), currency="EUR"),
                AccountOpeningBalance("TR", date(2026, 1, 1), Decimal("0"), currency="EUR"),
            ],
            account_transfers=[
                AccountTransfer(
                    date=date(2026, 1, 2),
                    source_account="ABANCA",
                    destination_account="TR",
                    amount=Decimal("100"),
                    currency="USD",
                )
            ],
        )
