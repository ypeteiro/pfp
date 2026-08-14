from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def test_root_route_uses_dashboard_v2():
    report = PortfolioReport(
        cash=Decimal("200"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1200"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("700"), fixed_income_value=Decimal("200"), gold_value=Decimal("100"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = WebApp(report).render("/")
    assert "Tu patrimonio" in html
    assert "Objetivo 75 / 20 / 5" in html
    assert "Cartera" in html
    assert "P/L total" in html


def test_dashboard_uses_full_asset_class_labels():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("0"), unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = WebApp(report).render("/")
    assert "Renta variable" in html
    assert "Renta fija" in html
    assert "Criptoactivos" in html
    assert "RV" not in html
    assert "RF" not in html


def test_dashboard_explains_financial_metrics_with_tooltips():
    report = PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("25"), unrealized_gain_loss=Decimal("75"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )
    html = WebApp(report).render("/")
    assert "Beneficios o pérdidas ya materializados mediante ventas realizadas." in html
    assert "Beneficios o pérdidas de posiciones que todavía mantienes abiertas." in html
    assert "Efectivo" in html
