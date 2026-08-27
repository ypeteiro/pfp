from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_series import PatrimonyPoint
from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
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


def test_dashboard_v2_colors_position_pnl_by_sign():
    positions = (
        PositionReport("POS", "Ganadora", "RV", Decimal("1"), Decimal("100"), Decimal("100"), Decimal("120"), Decimal("120"), Decimal("0.1"), Decimal("20"), isin="IE00TESTWIN"),
        PositionReport("NEG", "Perdedora", "RV", Decimal("1"), Decimal("100"), Decimal("100"), Decimal("80"), Decimal("80"), Decimal("0.1"), Decimal("-20"), isin="IE00TESTLOSS"),
    )
    report = PortfolioReport(
        cash=Decimal("0"), invested=Decimal("200"), market_value=Decimal("200"), total_value=Decimal("200"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("200"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=positions, accounts=(), movements=(),
    )
    html = dashboard_v2_html(report)
    assert '<td class="positive">20,00 €</td>' in html
    assert '<td class="negative">-20,00 €</td>' in html


def test_dashboard_v2_renders_distinct_patrimony_evolution_series_and_timeline():
    points = (
        PatrimonyPoint(datetime(2026, 1, 10), Decimal("1000"), Decimal("1000"), Decimal("0"), Decimal("0")),
        PatrimonyPoint(datetime(2026, 2, 10), Decimal("1800"), Decimal("1500"), Decimal("300"), Decimal("1200")),
        PatrimonyPoint(datetime(2026, 3, 10), Decimal("2400"), Decimal("2000"), Decimal("400"), Decimal("1700")),
    )
    report = PortfolioReport(
        cash=Decimal("700"), invested=Decimal("1700"), market_value=Decimal("1700"), total_value=Decimal("2400"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("400"),
        equity_value=Decimal("1700"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(), patrimony_series=points,
    )

    html = dashboard_v2_html(report)

    assert "Patrimonio" in html
    assert "Capital aportado" in html
    assert "Invertido" in html
    assert 'aria-label="Evolución temporal del patrimonio, capital aportado y dinero invertido"' in html
    assert "10/01/26" in html
    assert "10/02/26" in html
    assert "10/03/26" in html
    assert "1.000,00 €" in html
    assert "1.700,00 €" in html
    assert "2.400,00 €" in html
    assert "chart-grid" in html
    assert "chart-series patrimony" in html
    assert "chart-series contributed" in html
    assert "chart-series invested" in html
