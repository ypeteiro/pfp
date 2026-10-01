from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.server import dashboard_html


def test_dashboard_html_contains_core_sections():
    report = PortfolioReport(
        cash=Decimal("500"),
        invested=Decimal("1000"),
        market_value=Decimal("900"),
        total_value=Decimal("1400"),
        realized_gain_loss=Decimal("50"),
        unrealized_gain_loss=Decimal("-100"),
        equity_value=Decimal("675"),
        fixed_income_value=Decimal("180"),
        gold_value=Decimal("45"),
        crypto_value=Decimal("0"),
        positions=(),
    )
    html = dashboard_html(report)
    assert "Patrimonio total" in html
    assert "Efectivo" in html
    assert "Cartera invertida" in html
    assert "Asignación" in html
    assert "Posiciones" in html
    assert "75,00%" in html


def test_asset_lookup_payload_marks_found_result(monkeypatch):
    from pfp.web import server

    monkeypatch.setattr(
        server,
        "lookup_yahoo_asset",
        lambda isin: {"ticker": "BAC", "name": "Bank of America Corporation"},
    )

    assert server._asset_lookup_payload("US0605051046") == {
        "found": True,
        "ticker": "BAC",
        "name": "Bank of America Corporation",
    }


def test_asset_lookup_payload_marks_missing_result(monkeypatch):
    from pfp.web import server

    monkeypatch.setattr(server, "lookup_yahoo_asset", lambda isin: None)

    assert server._asset_lookup_payload("UNKNOWN") == {"found": False}
