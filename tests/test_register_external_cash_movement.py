from datetime import datetime, timezone
from decimal import Decimal

import pytest

from pfp.application.register_external_cash_movement import (
    RegisterExternalCashMovement,
    RegisterExternalCashMovementRequest,
)
from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio


def test_register_external_cash_movement_updates_existing_account_and_cash():
    portfolio = Portfolio(
        accounts=[
            Account(
                name="ABANCA Ahorro",
                broker="ABANCA",
                account_id="ABANCA_AHORRO",
                balance=Decimal("1000"),
            )
        ]
    )

    movement = RegisterExternalCashMovement().execute(
        portfolio,
        RegisterExternalCashMovementRequest(
            datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
            account_id="ABANCA_AHORRO",
            amount=Decimal("200"),
            description="Ingreso desde cuenta externa",
        ),
    )

    assert movement.amount == Decimal("200")
    assert portfolio.accounts[0].balance == Decimal("1200")
    assert portfolio.cash == Decimal("200")


def test_register_external_cash_movement_can_create_account():
    portfolio = Portfolio()

    RegisterExternalCashMovement().execute(
        portfolio,
        RegisterExternalCashMovementRequest(
            datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
            account_id="ABANCA_AHORRO",
            amount=Decimal("200"),
        ),
    )

    assert portfolio.accounts[0].account_id == "ABANCA_AHORRO"
    assert portfolio.accounts[0].balance == Decimal("200")
    assert portfolio.cash == Decimal("200")


def test_register_external_cash_movement_supports_outflow():
    portfolio = Portfolio(
        accounts=[
            Account(
                name="ABANCA Ahorro",
                broker="ABANCA",
                account_id="ABANCA_AHORRO",
                balance=Decimal("1000"),
            )
        ]
    )

    RegisterExternalCashMovement().execute(
        portfolio,
        RegisterExternalCashMovementRequest(
            datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
            account_id="ABANCA_AHORRO",
            amount=Decimal("-200"),
        ),
    )

    assert portfolio.accounts[0].balance == Decimal("800")
    assert portfolio.cash == Decimal("-200")


def test_register_external_cash_movement_rejects_currency_mismatch():
    portfolio = Portfolio(
        accounts=[
            Account(
                name="ABANCA Ahorro",
                broker="ABANCA",
                account_id="ABANCA_AHORRO",
                balance=Decimal("1000"),
            )
        ]
    )

    with pytest.raises(ValueError, match="currency does not match"):
        RegisterExternalCashMovement().execute(
            portfolio,
            RegisterExternalCashMovementRequest(
                datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
                account_id="ABANCA_AHORRO",
                amount=Decimal("200"),
                currency="USD",
            ),
        )


def test_register_external_cash_movement_rejects_zero_amount():
    with pytest.raises(ValueError, match="must not be zero"):
        RegisterExternalCashMovementRequest(
            datetime=datetime(2026, 9, 1, tzinfo=timezone.utc),
            account_id="ABANCA_AHORRO",
            amount=Decimal("0"),
        )
