from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.reporting.portfolio_report import PortfolioReport


def test_consolidated_net_worth_sums_account_cash_and_investments_without_double_counting_transfer():
    etf = Position(
        symbol="ETF",
        name="ETF",
        shares=Decimal("10"),
        invested=Decimal("1000"),
        average_price=Decimal("100"),
        portfolio_class="EQUITY",
        market_price=Decimal("120"),
    )
    portfolio = Portfolio(
        cash=Decimal("9000"),
        invested=Decimal("1000"),
        accounts=[
            Account("ABANCA Nómina", "ABANCA", balance=Decimal("3000"), account_id="ABANCA_NOMINA"),
            Account("ABANCA Ahorro", "ABANCA", balance=Decimal("3000"), account_id="ABANCA_AHORRO"),
            Account("Trade Republic", "Trade Republic", balance=Decimal("3000"), account_id="Trade Republic"),
        ],
        positions={"ETF": etf},
        account_positions={"Trade Republic": {"ETF": etf}},
    )

    report = PortfolioReport.from_portfolio(portfolio)

    assert report.cash == Decimal("9000")
    assert report.market_value == Decimal("1200")
    assert report.total_value == Decimal("10200")
    assert sum(account.balance for account in report.accounts) == Decimal("9000")
    assert sum(account.total_value for account in report.accounts if account.total_value is not None) == Decimal("10200")


def test_internal_transfer_changes_account_distribution_but_not_consolidated_net_worth():
    portfolio = Portfolio(
        cash=Decimal("10000"),
        accounts=[
            Account("ABANCA Ahorro", "ABANCA", balance=Decimal("4000"), account_id="ABANCA_AHORRO"),
            Account("Trade Republic", "Trade Republic", balance=Decimal("6000"), account_id="Trade Republic"),
        ],
    )

    report = PortfolioReport.from_portfolio(portfolio)

    assert [account.balance for account in report.accounts] == [Decimal("4000"), Decimal("6000")]
    assert sum(account.balance for account in report.accounts) == portfolio.cash == Decimal("10000")
    assert report.total_value == Decimal("10000")
