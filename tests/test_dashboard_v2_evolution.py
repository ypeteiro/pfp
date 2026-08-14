from datetime import datetime
from decimal import Decimal

from pfp.reporting.portfolio_report import MovementReport, PortfolioReport
from pfp.web.dashboard_ui import dashboard_v2_html


def test_dashboard_v2_shows_patrimony_evolution_from_capital_movements():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("100"),
        equity_value=Decimal("1000"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(
            MovementReport(datetime(2026, 1, 1), "TR", "CASH", "CONTRIBUTION", None, None, None, None, None, Decimal("1000"), Decimal("0"), Decimal("0"), "EUR", "Aportación", "c1"),
            MovementReport(datetime(2026, 2, 1), "TR", "CASH", "WITHDRAWAL", None, None, None, None, None, Decimal("100"), Decimal("0"), Decimal("0"), "EUR", "Retirada", "w1"),
        ),
    )
    html = dashboard_v2_html(report)
    for text in ("Evolución patrimonial", "Capital neto aportado", "1.000,00 €", "Aportaciones", "Retiradas", "Último flujo"):
        assert text in html
