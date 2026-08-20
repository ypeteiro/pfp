from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.reporting.portfolio_report import PortfolioReport


def test_account_report_preserves_account_identity_and_splits_values():
    portfolio = Portfolio(
        cash=Decimal("250"),
        invested=Decimal("500"),
        accounts=[
            Account("Savings", "ABANCA", balance=Decimal("1000"), account_id="ABANCA_AHORRO"),
            Account("Broker", "Trade Republic", balance=Decimal("250"), account_id="TR"),
        ],
        positions={"ETF": Position("ETF", "ETF", Decimal("5"), Decimal("500"), Decimal("100"), "EQUITY", Decimal("120"))},
        account_positions={"TR": {"ETF": Position("ETF", "ETF", Decimal("5"), Decimal("500"), Decimal("100"), "EQUITY", Decimal("120"))}},
    )

    report = PortfolioReport.from_portfolio(portfolio)
    by_id = {account.account_id: account for account in report.accounts}

    assert set(by_id) == {"ABANCA_AHORRO", "TR"}
    assert by_id["ABANCA_AHORRO"].balance == portfolio.accounts[0].balance
    assert by_id["ABANCA_AHORRO"].invested == Decimal("0")
    assert by_id["TR"].invested == portfolio.invested
    assert by_id["TR"].market_value == portfolio.market_value
    assert by_id["TR"].total_value == by_id["TR"].balance + by_id["TR"].market_value


def test_account_report_totals_are_derived_from_account_data_not_global_constants():
    portfolio = Portfolio(
        accounts=[
            Account("A", "Bank A", balance=Decimal("125"), account_id="A"),
            Account("B", "Bank B", balance=Decimal("275"), account_id="B"),
        ],
        account_positions={
            "A": {"X": Position("X", "X", Decimal("2"), Decimal("100"), Decimal("50"), "EQUITY", Decimal("60"))},
            "B": {"Y": Position("Y", "Y", Decimal("3"), Decimal("300"), Decimal("100"), "GOLD", Decimal("110"))},
        },
        positions={
            "X": Position("X", "X", Decimal("2"), Decimal("100"), Decimal("50"), "EQUITY", Decimal("60")),
            "Y": Position("Y", "Y", Decimal("3"), Decimal("300"), Decimal("100"), "GOLD", Decimal("110")),
        },
        cash=Decimal("400"),
        invested=Decimal("400"),
    )

    accounts = PortfolioReport.from_portfolio(portfolio).accounts

    assert sum(account.balance for account in accounts) == portfolio.cash
    assert sum(account.invested for account in accounts) == portfolio.invested
    assert sum(account.market_value or Decimal("0") for account in accounts) == portfolio.market_value
    assert sum(account.total_value or Decimal("0") for account in accounts) == portfolio.total_value


def test_account_report_handles_unpriced_account_position_without_inventing_market_value():
    portfolio = Portfolio(
        accounts=[Account("Broker", "Broker", balance=Decimal("100"), account_id="BROKER")],
        positions={"X": Position("X", "X", Decimal("1"), Decimal("100"), Decimal("100"), "EQUITY")},
        account_positions={"BROKER": {"X": Position("X", "X", Decimal("1"), Decimal("100"), Decimal("100"), "EQUITY")}},
        cash=Decimal("100"),
        invested=Decimal("100"),
    )

    account = PortfolioReport.from_portfolio(portfolio).accounts[0]

    assert account.invested == portfolio.invested
    assert account.market_value is None
    assert account.total_value is None
