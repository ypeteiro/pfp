from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def report():
    return PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )


def test_app_renders_sale_form():
    html = WebApp(report()).render("/sales/new")
    assert "Registrar venta" in html
    assert 'action="/sales"' in html
    assert 'name="operation_id"' in html
