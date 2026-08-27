from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_series import PatrimonyPoint
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard_ui import dashboard_v2_html


def test_dashboard_v2_shows_patrimony_evolution_from_historical_series():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("100"),
        equity_value=Decimal("1000"), fixed_income_value=Decimal("0"), gold_value=Decimal("0"), crypto_value=Decimal("0"),
        positions=(), accounts=(), patrimony_series=(
            PatrimonyPoint(datetime(2026, 1, 1), Decimal("1000"), Decimal("1000"), Decimal("0")),
            PatrimonyPoint(datetime(2026, 2, 1), Decimal("1100"), Decimal("1000"), Decimal("100")),
        ),
    )
    html = dashboard_v2_html(report)
    for text in ("Evolución patrimonial", "Patrimonio actual", "1.100,00 €", "Capital aportado", "Rendimiento acumulado", "01/02/2026"):
        assert text in html
