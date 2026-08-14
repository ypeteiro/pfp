from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.allocation_ui import allocation_html


def test_allocation_view_quantifies_rebalancing():
    report = PortfolioReport(
        cash=Decimal("0"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1000"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("700"), fixed_income_value=Decimal("250"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = allocation_html(report)
    for text in ("Renta variable", "Renta fija", "Objetivo", "Actual", "Desviación", "Valor objetivo", "Ajuste", "Aumentar", "Reducir", "750,00 €"):
        assert text in html
