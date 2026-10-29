from decimal import Decimal

from pfp.domain.asset import LONG_TERM, TACTICAL
from pfp.domain.asset_catalog import AssetCatalog
from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
from pfp.web.dashboard_ui import dashboard_v2_html


def test_vwce_is_long_term_and_stock_assets_are_tactical():
    assert AssetCatalog.get("IE00BK5BQT80").investment_strategy == LONG_TERM
    assert AssetCatalog.get("US55024U1097").investment_strategy == TACTICAL
    assert AssetCatalog.get("US1717793095").investment_strategy == TACTICAL


def test_dashboard_separates_long_term_and_tactical_equity():
    positions = (
        PositionReport("VWCE", "Vanguard FTSE All-World", "RV", Decimal("1"), Decimal("900"), Decimal("900"), Decimal("1000"), Decimal("1000"), Decimal("0.5"), Decimal("100"), ticker="VWCE", investment_strategy=LONG_TERM),
        PositionReport("VST", "Vistra", "RV", Decimal("1"), Decimal("300"), Decimal("300"), Decimal("400"), Decimal("400"), Decimal("0.2"), Decimal("100"), ticker="VST", investment_strategy=TACTICAL),
    )
    report = PortfolioReport(
        cash=Decimal("600"), invested=Decimal("1200"), market_value=Decimal("1400"), total_value=Decimal("2000"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("200"),
        equity_value=Decimal("1400"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=positions, accounts=(), movements=(),
    )

    html = dashboard_v2_html(report)

    assert report.long_term_equity_value == Decimal("1000")
    assert report.tactical_equity_value == Decimal("400")
    assert "Renta variable: largo vs corto plazo" in html
    assert "Largo plazo" in html
    assert "Corto plazo / táctico" in html
    assert "28,57%" in html
    assert "20,00% del patrimonio total" in html
    assert "Estrategia" in html
    assert "Corto plazo" in html
