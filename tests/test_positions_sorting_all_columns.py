from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
from pfp.web.app import WebApp
from pfp.web.positions_ui import positions_html


def report():
    return PortfolioReport(
        cash=Decimal("100"), invested=Decimal("3000"), market_value=Decimal("3300"), total_value=Decimal("3400"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("300"),
        equity_value=Decimal("2700"), fixed_income_value=Decimal("300"), gold_value=Decimal("300"), crypto_value=Decimal("0"),
        positions=(
            PositionReport("VWCE", "Vanguard FTSE All-World", "RV", Decimal("3"), Decimal("2000"), Decimal("666.67"), Decimal("800"), Decimal("0.80"), Decimal("200"), None, "IE00BK5BQT80", "VWCE"),
            PositionReport("EUNL", "MSCI World", "RV", Decimal("1"), Decimal("500"), Decimal("500"), Decimal("600"), Decimal("0.60"), Decimal("100"), None, "IE00B4L5Y983", "EUNL"),
            PositionReport("GOLD", "Gold", "ORO", Decimal("2"), Decimal("500"), Decimal("250"), Decimal("1000"), Decimal("1.00"), Decimal("0"), None, "IE00B4ND3602", "GOLD"),
        ),
        accounts=(), movements=(),
    )


def test_positions_can_sort_by_every_column():
    r = report()
    expected = {
        "symbol": ("EUNL", "GOLD", "VWCE"),
        "name": ("Gold", "MSCI World", "Vanguard FTSE All-World"),
        "class": ("Gold", "MSCI World", "Vanguard FTSE All-World"),
        "shares": ("EUNL", "GOLD", "VWCE"),
        "invested": ("GOLD", "EUNL", "VWCE"),
        "price": ("GOLD", "EUNL", "VWCE"),
        "value": ("EUNL", "VWCE", "GOLD"),
        "weight": ("EUNL", "VWCE", "GOLD"),
        "gain": ("GOLD", "EUNL", "VWCE"),
    }
    for field, symbols in expected.items():
        html = positions_html(r, field, "asc")
        order = [html.index(f">{symbol}<") for symbol in symbols]
        assert order == sorted(order), field
        assert f'href="/positions?sort={field}&direction=desc"' in html


def test_positions_sorting_is_available_from_webapp_route():
    html = WebApp(report()).render("/positions?sort=price&direction=asc")
    assert html.index(">GOLD<") < html.index(">EUNL<") < html.index(">VWCE<")
    assert 'href="/positions?sort=price&direction=desc"' in html
