from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.reporting.portfolio_report import PortfolioReport


def test_portfolio_report_exposes_totals_and_positions():
    portfolio = Portfolio(
        cash=Decimal("1000"),
        invested=Decimal("4000"),
        realized_gain_loss=Decimal("100"),
        positions={
            "EUNL": Position("EUNL", "MSCI World", Decimal("10"), Decimal("3000"), Decimal("300"), "RV", Decimal("330")),
            "GOLD": Position("GOLD", "Gold", Decimal("2"), Decimal("1000"), Decimal("500"), "GOLD", Decimal("550")),
        },
    )
    report = PortfolioReport.from_portfolio(portfolio)
    assert report.market_value == Decimal("4400")
    assert report.total_value == Decimal("5400")
    assert report.realized_gain_loss == Decimal("100")
    assert report.unrealized_gain_loss == Decimal("400")
    assert report.equity_value == Decimal("3300")
    assert report.gold_value == Decimal("1100")
    assert [p.symbol for p in report.positions] == ["EUNL", "GOLD"]


def test_portfolio_report_handles_missing_market_prices():
    portfolio = Portfolio(
        cash=Decimal("500"),
        invested=Decimal("1000"),
        positions={"EUNL": Position("EUNL", "MSCI World", Decimal("2"), Decimal("1000"), Decimal("500"), "RV")},
    )
    report = PortfolioReport.from_portfolio(portfolio)
    assert report.market_value == Decimal("0")
    assert report.total_value == Decimal("500")
    assert report.unrealized_gain_loss == Decimal("0")
    assert report.positions[0].market_value is None


def test_portfolio_report_account_totals_reconcile_with_consolidated_totals():
    first = Account("First", "Bank A", balance=Decimal("300"), account_id="FIRST")
    second = Account("Second", "Bank B", balance=Decimal("400"), account_id="SECOND")
    first_position = Position("EQUITY", "Equity", Decimal("2"), Decimal("200"), Decimal("100"), "EQUITY", Decimal("120"))
    second_position = Position("GOLD", "Gold", Decimal("3"), Decimal("150"), Decimal("50"), "GOLD", Decimal("60"))
    portfolio = Portfolio(
        cash=Decimal("700"),
        invested=Decimal("350"),
        accounts=[first, second],
        positions={
            "EQUITY": Position("EQUITY", "Equity", Decimal("2"), Decimal("200"), Decimal("100"), "EQUITY", Decimal("120")),
            "GOLD": Position("GOLD", "Gold", Decimal("3"), Decimal("150"), Decimal("50"), "GOLD", Decimal("60")),
        },
        account_positions={
            "FIRST": {"EQUITY": first_position},
            "SECOND": {"GOLD": second_position},
        },
    )

    report = PortfolioReport.from_portfolio(portfolio)

    assert sum(account.balance for account in report.accounts) == report.cash
    assert sum(account.invested for account in report.accounts) == report.invested
    assert sum(account.market_value or Decimal("0") for account in report.accounts) == report.market_value
    assert sum(account.total_value or Decimal("0") for account in report.accounts) == report.total_value
    assert {account.account_id for account in report.accounts} == {"FIRST", "SECOND"}


def test_portfolio_report_account_with_unpriced_position_has_no_total_value():
    account = Account("Unpriced", "Broker", balance=Decimal("250"), account_id="UNPRICED")
    position = Position("TEST", "Test", Decimal("2"), Decimal("100"), Decimal("50"), "EQUITY")
    portfolio = Portfolio(
        cash=Decimal("250"),
        invested=Decimal("100"),
        accounts=[account],
        positions={"TEST": Position("TEST", "Test", Decimal("2"), Decimal("100"), Decimal("50"), "EQUITY")},
        account_positions={"UNPRICED": {"TEST": position}},
    )

    report = PortfolioReport.from_portfolio(portfolio)

    account_report = report.accounts[0]
    assert account_report.account_id == "UNPRICED"
    assert account_report.balance == Decimal("250")
    assert account_report.invested == Decimal("100")
    assert account_report.market_value is None
    assert account_report.total_value is None
