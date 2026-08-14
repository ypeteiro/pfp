from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
from pfp.web.navigation import navigation_html
from pfp.web.positions_ui import positions_html


def report():
    return PortfolioReport(
        cash=Decimal("100"),
        invested=Decimal("1000"),
        market_value=Decimal("1200"),
        total_value=Decimal("1300"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("200"),
        equity_value=Decimal("1200"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(PositionReport(
            symbol="IE00B4L5Y983", name="MSCI World", portfolio_class="RV",
            shares=Decimal("2"), invested=Decimal("1000"), average_price=Decimal("500"),
            market_price=Decimal("600"), market_value=Decimal("1200"), weight=Decimal("1"),
            gain_loss=Decimal("200"), isin="IE00B4L5Y983", ticker="EUNL",
        ),),
    )


def test_position_price_explains_source_and_consultation_date():
    html = positions_html(report())
    assert "Yahoo Finance" in html
    assert "Fecha de consulta:" in html
    assert "Último precio disponible" in html


def test_navigation_includes_readme_link():
    html = navigation_html("/")
    assert "Ayuda / README" in html
    assert "target=\"_blank\"" in html
    assert "rel=\"noopener noreferrer\"" in html
