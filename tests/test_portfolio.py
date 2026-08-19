from datetime import datetime
from decimal import Decimal

import pytest

from pfp.domain.account import Account
from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.sale import Sale
from pfp.engine.portfolio_engine import PortfolioEngine


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


def test_account_can_have_explicit_stable_identity():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
        account_id="trade_republic",
    )

    assert account.id == "trade_republic"


def test_account_transfer_validates_basic_invariants():
    transfer = AccountTransfer(
        datetime=WHEN,
        source_account="abanca_nomina",
        destination_account="trade_republic",
        amount=Decimal("800"),
        currency="EUR",
    )

    assert transfer.amount == Decimal("800")

    with pytest.raises(ValueError, match="Transfer amount must be greater than zero"):
        AccountTransfer(WHEN, "abanca_nomina", "trade_republic", Decimal("0"), "EUR")

    with pytest.raises(ValueError, match="Source and destination accounts must differ"):
        AccountTransfer(WHEN, "abanca_nomina", "abanca_nomina", Decimal("1"), "EUR")


def test_portfolio_engine_moves_cash_between_accounts_without_changing_total_cash():
    opening_balances = [
        __import__("pfp.domain.account_opening_balance", fromlist=["AccountOpeningBalance"]).AccountOpeningBalance(
            account_id="abanca_nomina",
            date=WHEN.date(),
            amount=Decimal("1000"),
        )
    ]
    transfer = AccountTransfer(
        datetime=WHEN,
        source_account="abanca_nomina",
        destination_account="trade_republic",
        amount=Decimal("800"),
        currency="EUR",
    )

    portfolio = PortfolioEngine().build(
        [],
        opening_balances=opening_balances,
        account_transfers=[transfer],
    )

    balances = {account.id: account.balance for account in portfolio.accounts}
    assert balances == {
        "abanca_nomina": Decimal("200"),
        "trade_republic": Decimal("800"),
    }
    assert portfolio.cash == Decimal("1000")
    assert portfolio.invested == Decimal("0")
    assert portfolio.realized_gain_loss == Decimal("0")


def test_portfolio_engine_rejects_transfer_exceeding_source_cash():
    opening_balances = [
        __import__("pfp.domain.account_opening_balance", fromlist=["AccountOpeningBalance"]).AccountOpeningBalance(
            account_id="abanca_nomina",
            date=WHEN.date(),
            amount=Decimal("500"),
        )
    ]
    transfer = AccountTransfer(
        datetime=WHEN,
        source_account="abanca_nomina",
        destination_account="trade_republic",
        amount=Decimal("800"),
        currency="EUR",
    )

    with pytest.raises(ValueError, match="Transfer exceeds source account cash"):
        PortfolioEngine().build(
            [],
            opening_balances=opening_balances,
            account_transfers=[transfer],
        )


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
