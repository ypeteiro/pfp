from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def test_dashboard_layout_puts_allocation_and_distribution_side_by_side_and_positions_below():
    report = PortfolioReport(
        cash=Decimal("200"),
        invested=Decimal("1000"),
        market_value=Decimal("1000"),
        total_value=Decimal("1200"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("700"),
        fixed_income_value=Decimal("200"),
        gold_value=Decimal("100"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=(),
    )

    html = WebApp(report).render("/")

    assert ".dashboard-v2 > .two-col{grid-template-columns:1fr" in html
    assert ".dashboard-v2 > .two-col > article:first-child .allocation-carousel{display:grid;grid-template-columns:1fr 1fr" in html
    assert ".dashboard-v2 > .two-col > article:last-child{grid-column:1/-1" in html
    assert 'data-chart-slide="0"' in html
    assert 'data-chart-slide="1"' in html
    assert "Posiciones principales" in html
