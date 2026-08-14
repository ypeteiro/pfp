from datetime import datetime
from decimal import Decimal

from pfp.reporting.portfolio_report import MovementReport, PortfolioReport
from pfp.web.movements_ui import movements_html


def test_movements_view_shows_operation_details_and_totals():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("1000"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(
            MovementReport(datetime(2026, 8, 1, 10, 0), "Trade Republic", "TRADE", "BUY", "RV", "EUNL", "MSCI World", Decimal("2"), Decimal("500"), Decimal("-1000"), Decimal("2"), Decimal("0"), "EUR", "Compra ETF", "tx-1"),
            MovementReport(datetime(2026, 8, 2, 10, 0), "Trade Republic", "TRADE", "SELL", "RV", "EUNL", "MSCI World", Decimal("1"), Decimal("550"), Decimal("550"), Decimal("1"), Decimal("0"), "EUR", "Venta ETF", "tx-2"),
        ),
    )
    html = movements_html(report)
    for text in ("Movimientos", "Compras", "Ventas", "Comisiones", "TRADE", "BUY", "SELL", "Compra ETF", "1.000,00 €", "550,00 €"):
        assert text in html
