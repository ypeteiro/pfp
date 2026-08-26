from datetime import datetime
from decimal import Decimal

import pytest

from pfp.application.register_account_transfer import (
    RegisterAccountTransfer,
    RegisterAccountTransferRequest,
)
from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio


WHEN = datetime(2026, 8, 26, 10, 0)


def _portfolio() -> Portfolio:
    accounts = [
        Account("ABANCA", "ABANCA", account_id="abanca", balance=Decimal("1000")),
        Account("Trade Republic", "Trade Republic", account_id="trade_republic", balance=Decimal("200")),
    ]
    return Portfolio(accounts=accounts, account_positions={"abanca": {}, "trade_republic": {}})


def test_register_account_transfer_moves_cash_between_accounts_without_changing_total_account_cash():
    portfolio = _portfolio()
    initial_account_cash = sum(account.balance for account in portfolio.accounts)

    transfer = RegisterAccountTransfer().execute(
        portfolio,
        RegisterAccountTransferRequest(WHEN, "abanca", "trade_republic", Decimal("300")),
    )

    assert transfer.source_account == "abanca"
    assert portfolio.accounts[0].balance == Decimal("700")
    assert portfolio.accounts[1].balance == Decimal("500")
    assert sum(account.balance for account in portfolio.accounts) == initial_account_cash


def test_register_account_transfer_rejects_insufficient_source_cash():
    portfolio = _portfolio()

    with pytest.raises(ValueError, match="Insufficient cash"):
        RegisterAccountTransfer().execute(
            portfolio,
            RegisterAccountTransferRequest(WHEN, "abanca", "trade_republic", Decimal("1001")),
        )
