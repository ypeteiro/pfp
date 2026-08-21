from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.account_transfer import AccountTransfer
from pfp.engine.portfolio_engine import PortfolioEngine


def test_account_transfer_preserves_consolidated_cash_and_moves_value_between_accounts():
    transfer = AccountTransfer(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        source_account="ABANCA_NOMINA",
        destination_account="Trade Republic",
        amount=Decimal("1000"),
        currency="EUR",
    )

    portfolio = PortfolioEngine().build(
        [],
        opening_balances=[
            AccountOpeningBalance("ABANCA_NOMINA", datetime(2026, 1, 1, tzinfo=timezone.utc).date(), Decimal("5000")),
            AccountOpeningBalance("Trade Republic", datetime(2026, 1, 1, tzinfo=timezone.utc).date(), Decimal("5000")),
        ],
        account_transfers=[transfer],
    )

    accounts = {account.account_id: account for account in portfolio.accounts}

    assert accounts["ABANCA_NOMINA"].balance == Decimal("4000")
    assert accounts["Trade Republic"].balance == Decimal("6000")
    assert sum(account.balance for account in portfolio.accounts) == Decimal("10000")
    assert portfolio.cash == Decimal("10000")
    assert portfolio.invested == Decimal("0")
    assert portfolio.positions == {}
