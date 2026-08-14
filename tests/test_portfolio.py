from datetime import datetime
from decimal import Decimal

import pytest

from pfp.domain.account import Account
from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.sale import Sale


WHEN = datetime(2026, 1, 1)


def test_portfolio_can_contain_accounts():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
        currency="EUR",
        balance=Decimal("3603.39"),
    )

    portfolio = Portfolio(accounts=[account])

    assert len(portfolio.accounts) == 1
    assert portfolio.accounts[0].name == "Trade Republic"
    assert portfolio.accounts[0].balance == Decimal("3603.39")


def test_contribution_increases_cash_and_withdrawal_reduces_it():
    portfolio = Portfolio()

    portfolio.add_capital_flow(CapitalFlow(WHEN, Decimal("1000"), FlowType.CONTRIBUTION))
    portfolio.add_capital_flow(CapitalFlow(WHEN, Decimal("250"), FlowType.WITHDRAWAL))

    assert portfolio.cash == Decimal("750")


def test_withdrawal_cannot_exceed_cash():
    portfolio = Portfolio(cash=Decimal("100"))

    with pytest.raises(ValueError, match="Withdrawal exceeds portfolio cash"):
        portfolio.add_capital_flow(
            CapitalFlow(WHEN, Decimal("101"), FlowType.WITHDRAWAL)
        )


def test_investment_moves_cash_into_a_position():
    portfolio = Portfolio(cash=Decimal("1000"))
    investment = Investment(
        datetime=WHEN,
        symbol="EUNL",
        shares=Decimal("4"),
        amount=Decimal("400"),
        price=Decimal("100"),
        portfolio_class="RV",
    )

    portfolio.add_investment(investment)

    assert portfolio.cash == Decimal("600")
    assert portfolio.invested == Decimal("400")
    assert portfolio.positions["EUNL"].shares == Decimal("4")
    assert portfolio.positions["EUNL"].average_price == Decimal("100")


def test_multiple_investments_use_weighted_average_price():
    portfolio = Portfolio(cash=Decimal("1000"))

    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("4"), Decimal("400"), Decimal("100"), "RV")
    )
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("2"), Decimal("240"), Decimal("120"), "RV")
    )

    position = portfolio.positions["EUNL"]
    assert position.shares == Decimal("6")
    assert position.invested == Decimal("640")
    assert position.average_price == Decimal("640") / Decimal("6")


def test_sale_reduces_position_and_records_realized_gain():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("4"), Decimal("400"), Decimal("100"), "RV")
    )

    portfolio.add_sale(
        Sale(WHEN, "EUNL", Decimal("2"), Decimal("240"), Decimal("120"))
    )

    position = portfolio.positions["EUNL"]
    assert portfolio.cash == Decimal("840")
    assert portfolio.invested == Decimal("200")
    assert portfolio.realized_gain_loss == Decimal("40")
    assert position.shares == Decimal("2")
    assert position.invested == Decimal("200")
    assert position.average_price == Decimal("100")


def test_sale_cannot_exceed_position():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("2"), Decimal("200"), Decimal("100"), "RV")
    )

    with pytest.raises(ValueError, match="Sale shares exceed current position"):
        portfolio.add_sale(
            Sale(WHEN, "EUNL", Decimal("3"), Decimal("330"), Decimal("110"))
        )
