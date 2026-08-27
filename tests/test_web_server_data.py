from decimal import Decimal
from pathlib import Path

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.server import build_web_report


class FakePriceProvider:
    def get_prices(self, symbols):
        assert symbols == ["EUNL"]
        return {"EUNL": Decimal("600")}


def test_build_web_report_uses_consolidated_loader_and_market_prices(monkeypatch):
    portfolio = Portfolio(
        positions={
            "EUNL": Position(
                "EUNL", "MSCI World", Decimal("2"), Decimal("1000"), Decimal("500"), "EQUITY"
            )
        },
        cash=Decimal("100"),
        invested=Decimal("1000"),
        realized_gain_loss=Decimal("50"),
    )

    calls = []

    def fake_load_portfolio(movements_file, investments_file, sales_file):
        calls.append((movements_file, investments_file, sales_file))
        return portfolio

    monkeypatch.setattr("pfp.web.server.load_portfolio", fake_load_portfolio)
    monkeypatch.setattr("pfp.web.server._trade_republic_cash_movements", lambda movements_file: [])

    report = build_web_report(
        Path("movements.csv"),
        Path("investments.csv"),
        Path("sales.csv"),
        FakePriceProvider(),
    )

    assert isinstance(report, PortfolioReport)
    assert calls == [(Path("movements.csv"), Path("investments.csv"), Path("sales.csv"))]
    assert report.invested == Decimal("1000")
    assert report.realized_gain_loss == Decimal("50")
    assert report.market_value == Decimal("1200")
    assert report.positions[0].market_value == Decimal("1200")
    assert report.positions[0].weight == Decimal("1")
