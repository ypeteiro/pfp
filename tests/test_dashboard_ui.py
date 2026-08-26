from decimal import Decimal

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
