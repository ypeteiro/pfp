from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def test_root_route_uses_dashboard_v2():
    report = PortfolioReport(
        cash=Decimal("200"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1200"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("700"), fixed_income_value=Decimal("200"), gold_value=Decimal("100"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = WebApp(report).render("/")
    assert "Tu patrimonio" in html
    assert "Objetivo 75 / 20 / 5" in html
    assert "Cartera" in html
    assert "P/L total" in html
