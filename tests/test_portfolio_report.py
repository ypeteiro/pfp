from decimal import Decimal

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
