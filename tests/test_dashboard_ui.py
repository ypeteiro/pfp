from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard_ui import dashboard_v2_html


def test_dashboard_v2_shows_strategy_and_main_metrics():
    report = PortfolioReport(
        cash=Decimal("200"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1200"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("700"), fixed_income_value=Decimal("200"), gold_value=Decimal("100"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = dashboard_v2_html(report)
    assert "Tu patrimonio" in html
    assert "75 / 20 / 5" in html
    assert "allocation-panel-heading" in html
    assert "70,00%" in html
    assert "Aumentar" in html
    assert "1.200,00 €" in html
    assert "30,00 €" in html
