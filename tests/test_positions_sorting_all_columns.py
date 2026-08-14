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
            PositionReport(
                symbol="VWCE", name="Vanguard FTSE All-World", portfolio_class="RV",
                shares=Decimal("3"), invested=Decimal("2000"), average_price=Decimal("666.67"),
                market_price=Decimal("666.67"), market_value=Decimal("2000"), weight=Decimal("0.80"),
                gain_loss=Decimal("200"), isin="IE00BK5BQT80", ticker="VWCE",
            ),
            PositionReport(
                symbol="EUNL", name="MSCI World", portfolio_class="RV",
                shares=Decimal("1"), invested=Decimal("500"), average_price=Decimal("500"),
                market_price=Decimal("500"), market_value=Decimal("500"), weight=Decimal("0.60"),
                gain_loss=Decimal("100"), isin="IE00B4L5Y983", ticker="EUNL",
            ),
            PositionReport(
                symbol="GOLD", name="Gold", portfolio_class="GOLD",
                shares=Decimal("2"), invested=Decimal("500"), average_price=Decimal("250"),
                market_price=Decimal("250"), market_value=Decimal("500"), weight=Decimal("1.00"),
                gain_loss=Decimal("0"), isin="IE00B4ND3602", ticker="GOLD",
            ),
        ),
        accounts=(), movements=(),
    )


def test_positions_can_sort_by_every_column():
    r = report()
    expected = {
        "symbol": ("EUNL", "GOLD", "VWCE"),
        "name": ("GOLD", "EUNL", "VWCE"),
        "class": ("GOLD", "EUNL", "VWCE"),
        "shares": ("EUNL", "GOLD", "VWCE"),
        "invested": ("EUNL", "GOLD", "VWCE"),
        "price": ("GOLD", "EUNL", "VWCE"),
        "value": ("EUNL", "GOLD", "VWCE"),
        "weight": ("EUNL", "VWCE", "GOLD"),
        "gain": ("GOLD", "EUNL", "VWCE"),
    }
    for field, symbols in expected.items():
        html = positions_html(r, field, "asc")
        order = [html.index(f'<strong>{symbol}</strong>') for symbol in symbols]
        assert order == sorted(order), field
        assert f'href="/positions?sort={field}&direction=desc"' in html


def test_positions_sorting_is_available_from_webapp_route():
    html = WebApp(report()).render("/positions?sort=price&direction=asc")
    assert html.index("<strong>GOLD</strong>") < html.index("<strong>EUNL</strong>") < html.index("<strong>VWCE</strong>")
    assert 'href="/positions?sort=price&direction=desc"' in html
