from datetime import date
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.portfolio import Portfolio


def test_account_transfer_preserves_consolidated_cash_and_moves_value_between_accounts():
    portfolio = Portfolio(cash=Decimal("10000"))
    portfolio.accounts = [
        Account(name="ABANCA nómina", broker="ABANCA", currency="EUR", balance=Decimal("5000"), account_id="ABANCA_NOMINA"),
        Account(name="Trade Republic", broker="Trade Republic", currency="EUR", balance=Decimal("5000"), account_id="Trade Republic"),
    ]

    transfer = AccountTransfer(
        transfer_date=date(2026, 8, 10),
        source_account_id="ABANCA_NOMINA",
        destination_account_id="Trade Republic",
        amount=Decimal("1000"),
        currency="EUR",
        description="Monthly investment transfer",
    )

    before = sum(account.balance for account in portfolio.accounts)
    transfer.apply(portfolio)
    after = sum(account.balance for account in portfolio.accounts)

    assert portfolio.accounts[0].balance == Decimal("4000")
    assert portfolio.accounts[1].balance == Decimal("6000")
    assert before == after == Decimal("10000")
    assert portfolio.cash == Decimal("10000")
