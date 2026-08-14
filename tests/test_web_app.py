from decimal import Decimal

import pytest

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def report():
    return PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )


def test_app_routes_main_sections():
    app = WebApp(report())
    assert "Dashboard" in app.render("/")
    assert "Posiciones" in app.render("/positions")
    assert "Movimientos" in app.render("/movements")
    assert "Asignación" in app.render("/allocation")


def test_app_marks_navigation_and_rejects_unknown_route():
    html = WebApp(report()).render("/positions")
    assert 'href="/positions"' in html
    assert 'aria-current="page" class="active"' in html
    with pytest.raises(KeyError):
        WebApp(report()).render("/unknown")
