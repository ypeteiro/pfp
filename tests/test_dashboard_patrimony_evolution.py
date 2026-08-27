from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_series import PatrimonyPoint
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard_ui import dashboard_v2_html


def test_dashboard_renders_real_patrimony_evolution():
    points = (
        PatrimonyPoint(datetime(2026, 1, 1, 10), Decimal("1000"), Decimal("1000"), Decimal("0")),
        PatrimonyPoint(datetime(2026, 2, 1, 10), Decimal("1120"), Decimal("1000"), Decimal("120")),
    )
    report = PortfolioReport(
        cash=Decimal("0"),
        invested=Decimal("1000"),
        market_value=Decimal("1120"),
        total_value=Decimal("1120"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("120"),
        equity_value=Decimal("1120"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(),
        patrimony_series=points,
    )

    html = dashboard_v2_html(report)

    assert "Patrimonio actual" in html
    assert "1.120,00 €" in html
    assert "Capital aportado" in html
    assert "1.000,00 €" in html
    assert "Rendimiento acumulado" in html
    assert "120,00 €" in html
    assert "patrimony-chart" in html
