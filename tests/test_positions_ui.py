from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
from pfp.web.positions_ui import positions_html


def test_positions_view_shows_financial_details():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1200"), total_value=Decimal("1300"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("200"),
        equity_value=Decimal("1200"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(PositionReport(
            symbol="EUNL",
            name="MSCI World",
            portfolio_class="RV",
            shares=Decimal("2"),
            invested=Decimal("1000"),
            average_price=Decimal("500"),
            market_price=Decimal("600"),
            market_value=Decimal("1200"),
            weight=Decimal("0.8"),
            gain_loss=Decimal("200"),
            isin="IE00B4L5Y983",
            ticker="EUNL",
        ),),
        accounts=(), movements=(),
    )
    html = positions_html(report)
    for text in ("MSCI World", "Invertido", "Precio", "Valor", "Peso", "P/L", "80,00%", "200,00 €"):
        assert text in html
