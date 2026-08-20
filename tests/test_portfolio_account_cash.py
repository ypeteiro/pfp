from datetime import date, datetime, timezone
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.domain.sale import Sale
from pfp.engine.portfolio_engine import PortfolioEngine


def _investment(*, account_id=None, amount="200", shares="2"):
    return Investment(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal(shares),
        amount=Decimal(amount),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        account_id=account_id,
    )


def _sale(*, account_id=None, amount="150", shares="1"):
    return Sale(
        datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal(shares),
        amount=Decimal(amount),
        price=Decimal("150"),
        account_id=account_id,
    )


def _opening(account_id, amount):
    return AccountOpeningBalance(
        account_id=account_id,
        date=date(2026, 8, 1),
        amount=Decimal(amount),
    )


def test_build_persisted_investment_reduces_its_account_cash():
    portfolio = PortfolioEngine().build(
        movements=[],
        opening_balances=[_opening("ABANCA_AHORRO", "1000")],
        investments=[_investment(account_id="ABANCA_AHORRO")],
    )

    accounts = {account.account_id: account for account in portfolio.accounts}

    assert accounts["ABANCA_AHORRO"].balance == Decimal("800")
    assert portfolio.cash == Decimal("800")


def test_build_persisted_sale_increases_its_account_cash_and_consolidated_cash():
    portfolio = PortfolioEngine().build(
        movements=[],
        opening_balances=[
            _opening("Trade Republic", "1000"),
            _opening("ABANCA_AHORRO", "500"),
        ],
        investments=[_investment(account_id="Trade Republic")],
        sales=[_sale(account_id="Trade Republic")],
    )

    accounts = {account.account_id: account for account in portfolio.accounts}

    assert accounts["Trade Republic"].balance == Decimal("950")
    assert accounts["ABANCA_AHORRO"].balance == Decimal("500")
    assert portfolio.cash == Decimal("1450")
    assert portfolio.invested == Decimal("100")


def test_apply_sale_updates_account_cash_and_consolidated_cash():
    portfolio = Portfolio(
        accounts=[
            Account(
                name="Trade Republic",
                broker="Trade Republic",
                account_id="Trade Republic",
                balance=Decimal("800"),
            )
        ],
        positions={
            "TEST": Position(
                symbol="TEST",
                name="TEST",
                shares=Decimal("2"),
                invested=Decimal("200"),
                average_price=Decimal("100"),
                portfolio_class="EQUITY",
            )
        },
        cash=Decimal("800"),
        invested=Decimal("200"),
    )

    PortfolioEngine().apply_sale(portfolio, _sale(account_id="Trade Republic"))

    assert portfolio.accounts[0].balance == Decimal("950")
    assert portfolio.cash == Decimal("950")
    assert portfolio.invested == Decimal("100")
    assert portfolio.realized_gain_loss == Decimal("50")
