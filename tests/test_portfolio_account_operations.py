from datetime import date, datetime, timezone
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.investment import Investment
from pfp.domain.movement import Movement
from pfp.domain.sale import Sale
from pfp.domain.portfolio import Portfolio
from pfp.engine.portfolio_engine import PortfolioEngine


def _buy_movement(account_id="ABANCA_AHORRO"):
    return Movement(
        datetime=datetime(2026, 8, 1, tzinfo=timezone.utc),
        date=date(2026, 8, 1),
        account_type="DEFAULT",
        account_id=account_id,
        broker="ABANCA_AHORRO",
        category="CASH",
        type="BUY",
        asset_class="EQUITY",
        name="Test Asset",
        symbol="TEST",
        shares=Decimal("1"),
        price=Decimal("100"),
        amount=Decimal("100"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description="Test buy",
        transaction_id="test-account-buy",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )


def test_build_applies_persisted_investment_to_its_account_cash():
    investment = Investment(
        datetime=datetime(2026, 8, 2, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        broker="ABANCA_AHORRO",
        account_id="ABANCA_AHORRO",
    )

    portfolio = PortfolioEngine().build(
        [],
        investments=[investment],
        opening_balances=[
            AccountOpeningBalance("ABANCA_AHORRO", date(2026, 1, 1), Decimal("1000"))
        ],
    )

    account = portfolio.accounts[0]
    assert account.account_id == "ABANCA_AHORRO"
    assert account.balance == Decimal("800")
    assert portfolio.cash == Decimal("800")


def test_build_applies_persisted_sale_to_its_account_cash():
    sale = Sale(
        datetime=datetime(2026, 8, 2, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("0.5"),
        amount=Decimal("150"),
        price=Decimal("300"),
        broker="ABANCA_AHORRO",
        account_id="ABANCA_AHORRO",
    )

    portfolio = PortfolioEngine().build(
        [_buy_movement()],
        sales=[sale],
        opening_balances=[
            AccountOpeningBalance("ABANCA_AHORRO", date(2026, 1, 1), Decimal("1000"))
        ],
    )

    account = portfolio.accounts[0]
    assert account.balance == Decimal("1050")
    assert portfolio.cash == Decimal("1050")


def test_apply_investment_updates_the_target_account_balance():
    portfolio = Portfolio()
    portfolio.accounts = [
        Account(
            name="ABANCA_AHORRO",
            broker="ABANCA_AHORRO",
            currency="EUR",
            balance=Decimal("1000"),
            account_id="ABANCA_AHORRO",
        )
    ]
    portfolio.cash = Decimal("1000")
    investment = Investment(
        datetime=datetime(2026, 8, 2, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        broker="ABANCA_AHORRO",
        account_id="ABANCA_AHORRO",
    )

    PortfolioEngine().apply_investment(portfolio, investment)

    assert portfolio.cash == Decimal("800")
    assert portfolio.accounts[0].balance == Decimal("800")
