from decimal import Decimal
from pathlib import Path

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.server import build_web_report


class FakeImporter:
    def load(self, path):
        return []


class FakeRepository:
    def __init__(self, path):
        self.path = path

    def load(self):
        return ["data"]


class FakePriceProvider:
    def get_prices(self, symbols):
        assert symbols == ["EUNL"]
        return {"EUNL": Decimal("600")}


def test_build_web_report_uses_investments_sales_and_market_prices(monkeypatch):
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

    class FakeEngine:
        calls = []

        def build(self, movements, prices=None, investments=None, sales=None):
            self.calls.append((prices, investments, sales))
            if prices is None:
                return portfolio
            valued = Portfolio(
                positions={
                    "EUNL": Position(
                        "EUNL", "MSCI World", Decimal("2"), Decimal("1000"), Decimal("500"), "EQUITY",
                        market_price=prices["EUNL"],
                    )
                },
                cash=Decimal("100"),
                invested=Decimal("1000"),
                realized_gain_loss=Decimal("50"),
            )
            return valued

    monkeypatch.setattr("pfp.web.server.TradeRepublicImporter", FakeImporter)
    monkeypatch.setattr("pfp.web.server.InvestmentRepository", FakeRepository)
    monkeypatch.setattr("pfp.web.server.SaleRepository", FakeRepository)
    monkeypatch.setattr("pfp.web.server.PortfolioEngine", FakeEngine)

    report = build_web_report(Path("movements.csv"), Path("investments.csv"), Path("sales.csv"), FakePriceProvider())

    assert isinstance(report, PortfolioReport)
    assert report.invested == Decimal("1000")
    assert report.realized_gain_loss == Decimal("50")
    assert report.market_value == Decimal("1200")
    assert report.positions[0].market_value == Decimal("1200")
    assert report.positions[0].weight == Decimal("1")
