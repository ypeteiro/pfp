from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport, PositionReport
from pfp.web.app import WebApp


def make_report() -> PortfolioReport:
    return PortfolioReport(
        cash=Decimal("200"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1200"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("700"), fixed_income_value=Decimal("200"), gold_value=Decimal("100"), crypto_value=Decimal("0"),
        positions=(
            PositionReport("EUNL", "MSCI World", "RV", Decimal("2"), Decimal("500"), Decimal("600"), Decimal("600"), Decimal("0.60"), Decimal("100"), None, "IE00B4L5Y983", "EUNL"),
            PositionReport("VWCE", "Vanguard FTSE All-World", "RV", Decimal("1"), Decimal("400"), Decimal("400"), Decimal("400"), Decimal("0.40"), Decimal("0"), None, "IE00BK5BQT80", "VWCE"),
        ),
        accounts=(), movements=(),
    )


def test_root_route_uses_dashboard_v2():
    html = WebApp(make_report()).render("/")
    assert "Tu patrimonio" in html
    assert "Objetivo 75 / 20 / 5" in html
    assert "Cartera" in html
    assert "P/L total" in html
    assert html.count("24.966,47 €") == 0
    assert "hero-value" not in html


def test_dashboard_uses_full_asset_class_labels():
    report = make_report()
    html = WebApp(report).render("/")
    assert "Renta variable" in html
    assert "Renta fija" in html
    assert "Criptoactivos" in html
    assert "RV" not in html
    assert "RF" not in html


def test_dashboard_explains_financial_metrics_with_tooltips():
    report = make_report()
    html = WebApp(report).render("/")
    assert "Beneficios o pérdidas ya materializados mediante ventas realizadas." in html
    assert "Beneficios o pérdidas de posiciones que todavía mantienes abiertas." in html
    assert "Efectivo" in html


def test_dashboard_positions_can_sort_by_name_and_value():
    report = make_report()
    by_name = WebApp(report).render("/?sort=name&direction=asc")
    assert by_name.index("MSCI World") < by_name.index("Vanguard FTSE All-World")
    assert 'href="/?sort=name&direction=desc"' in by_name

    by_value = WebApp(report).render("/?sort=value&direction=asc")
    assert by_value.index("Vanguard FTSE All-World") < by_value.index("MSCI World")
    assert 'href="/?sort=value&direction=desc"' in by_value


def test_dashboard_positions_can_sort_by_weight():
    report = make_report()
    html = WebApp(report).render("/?sort=weight&direction=asc")
    assert html.index("Vanguard FTSE All-World") < html.index("MSCI World")
    assert 'href="/?sort=weight&direction=desc"' in html
