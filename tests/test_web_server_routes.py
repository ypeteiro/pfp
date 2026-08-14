from decimal import Decimal
from pathlib import Path

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def test_server_uses_routed_app_for_all_sections():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    app = WebApp(report)
    for path, heading in (("/", "Dashboard"), ("/positions", "Posiciones"), ("/movements", "Movimientos"), ("/allocation", "Asignación")):
        assert heading in app.render(path)
