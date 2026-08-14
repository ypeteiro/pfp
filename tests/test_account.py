from decimal import Decimal

import pytest

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


@pytest.mark.parametrize("name", ["", "   "])
def test_account_rejects_empty_name(name):
    with pytest.raises(ValueError, match="Account name"):
        Account(name, "Trade Republic")


def test_account_rejects_empty_broker():
    with pytest.raises(ValueError, match="Account broker"):
        Account("Cuenta", "   ")


@pytest.mark.parametrize("currency", ["eur", "EU", "EURO", "E1R", "€UR"])
def test_account_rejects_invalid_currency(currency):
    with pytest.raises(ValueError, match="Currency"):
        Account("Cuenta", "Trade Republic", currency)
