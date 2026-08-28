from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_series import PatrimonyPoint
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


def test_dashboard_v2_renders_readable_patrimony_evolution_series_and_timeline():
    report = PortfolioReport(
        cash=Decimal("200"), invested=Decimal("1000"), market_value=Decimal("1200"), total_value=Decimal("1400"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("200"),
        equity_value=Decimal("1200"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
        patrimony_series=(
            PatrimonyPoint(datetime(2026, 7, 1), Decimal("1000"), Decimal("1000"), Decimal("0"), Decimal("1000"), Decimal("1000")),
            PatrimonyPoint(datetime(2026, 8, 1), Decimal("1400"), Decimal("1200"), Decimal("200"), Decimal("1000"), Decimal("1200")),
        ),
    )

    html = dashboard_v2_html(report)

    assert "patrimony-chart" in html
    assert "Patrimonio" in html
    assert "Capital aportado" in html
    assert "Capital invertido" in html
    assert "01/07/26" in html
    assert "01/08/26" in html
    assert "Patrimonio actual" in html
    assert "Capital invertido · 1.000,00 €" in html
