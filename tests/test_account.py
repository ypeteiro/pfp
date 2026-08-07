from decimal import Decimal

from pfp.domain.account import Account


def test_account_defaults():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
    )

    assert account.name == "Trade Republic"
    assert account.broker == "Trade Republic"
    assert account.currency == "EUR"
    assert account.balance == Decimal("0")


def test_account_with_balance():
    account = Account(
        name="ABANCA Remunerada",
        broker="ABANCA",
        currency="EUR",
        balance=Decimal("31106"),
    )

    assert account.balance == Decimal("31106")
    assert account.currency == "EUR"