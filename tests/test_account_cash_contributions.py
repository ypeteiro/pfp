from decimal import Decimal

from pfp.application.register_external_cash_movement import (
    RegisterExternalCashMovement,
    RegisterExternalCashMovementRequest,
)
from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio


def _portfolio() -> Portfolio:
    account = Account(
        name="ABANCA",
        broker="ABANCA",
        currency="EUR",
        account_id="abanca",
        balance=Decimal("0"),
    )
    return Portfolio(accounts=[account], account_positions={"abanca": {}})


def test_external_cash_contribution_increases_account_and_portfolio_cash() -> None:
    portfolio = _portfolio()
    use_case = RegisterExternalCashMovement()

    use_case.execute(
        portfolio,
        RegisterExternalCashMovementRequest(
            datetime=__import__("datetime").datetime(2026, 8, 26, 10, 0),
            account_id="abanca",
            amount=Decimal("1000"),
        ),
    )

    assert portfolio.accounts[0].balance == Decimal("1000")
    assert portfolio.cash == Decimal("1000")


def test_external_cash_contribution_is_not_created_by_an_account_transfer() -> None:
    portfolio = _portfolio()
    portfolio.accounts.append(
        Account(
            name="Trade Republic",
            broker="Trade Republic",
            currency="EUR",
            account_id="trade_republic",
            balance=Decimal("0"),
        )
    )
    portfolio.account_positions["trade_republic"] = {}

    initial_total = sum(account.balance for account in portfolio.accounts)
    transfer_amount = Decimal("800")

    portfolio.accounts[0].balance += transfer_amount
    portfolio.accounts[1].balance -= transfer_amount

    final_total = sum(account.balance for account in portfolio.accounts)

    assert final_total == initial_total
