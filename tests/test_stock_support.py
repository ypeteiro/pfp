from datetime import date, datetime, timezone
from decimal import Decimal

import pandas as pd

from pfp.domain.asset_catalog import AssetCatalog
from pfp.domain.movement import Movement
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.market import yahoo


def _movement(*, asset_class="STOCK", symbol="US55024U1097", name="Lumentum Holdings"):
    return Movement(
        datetime=datetime(2026, 8, 17, 10, 30, tzinfo=timezone.utc),
        date=date(2026, 8, 17),
        account_type="DEFAULT",
        broker="Trade Republic",
        category="CASH",
        type="BUY",
        asset_class=asset_class,
        name=name,
        symbol=symbol,
        shares=Decimal("1"),
        price=Decimal("100"),
        amount=Decimal("100"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description=None,
        transaction_id="stock-test",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )


def test_asset_catalog_knows_new_stocks():
    lumentum = AssetCatalog.get("US55024U1097")
    ciena = AssetCatalog.get("US1717793095")
    assert lumentum is not None
    assert lumentum.portfolio_class == "STOCK"
    assert lumentum.ticker == "LITE"
    assert ciena is not None
    assert ciena.portfolio_class == "STOCK"
    assert ciena.ticker == "CIEN"


def test_asset_catalog_preserves_imported_class_for_unknown_asset():
    asset = AssetCatalog.get_or_create("US0000000000", "Example Stock", "STOCK")
    assert asset.portfolio_class == "STOCK"


def test_portfolio_engine_uses_stock_class_from_trade_republic():
    portfolio = Portfolio(cash=Decimal("200"))
    portfolio = PortfolioEngine().build([_movement()], prices={"US55024U1097": Decimal("120")})
    position = portfolio.positions["US55024U1097"]
    assert position.portfolio_class == "STOCK"
    assert position.market_price == Decimal("120")
    assert position.market_value == Decimal("120")


def test_portfolio_report_normalizes_stock_to_equity_and_handles_missing_price():
    portfolio = Portfolio(
        cash=Decimal("100"),
        invested=Decimal("100"),
        positions={
            "US55024U1097": Position("US55024U1097", "Lumentum Holdings", Decimal("1"), Decimal("100"), Decimal("100"), "STOCK"),
            "UNKNOWN": Position("UNKNOWN", "Unknown", Decimal("1"), Decimal("50"), Decimal("50"), "STOCK"),
        },
    )
    portfolio.positions["US55024U1097"].market_price = Decimal("120")
    report = PortfolioReport.from_portfolio(portfolio)
    assert report.equity_value == Decimal("120")
    assert report.positions[0].portfolio_class == "RV"
    unknown = next(position for position in report.positions if position.symbol == "UNKNOWN")
    assert unknown.market_value is None
    assert unknown.weight is None


def test_trade_republic_importer_converts_empty_asset_class_to_none(tmp_path):
    columns = [
        "datetime", "date", "account_type", "category", "type", "asset_class", "name", "symbol", "shares", "price", "amount", "fee", "tax", "currency", "original_amount", "original_currency", "fx_rate", "description", "transaction_id", "counterparty_name", "counterparty_iban", "payment_reference", "mcc_code",
    ]
    row = {
        "datetime": "2026-08-17T10:30:00Z", "date": "2026-08-17", "account_type": "DEFAULT", "category": "CASH", "type": "TRANSFER_INSTANT_INBOUND", "asset_class": "", "name": "", "symbol": "", "shares": "", "price": "", "amount": "100", "fee": "", "tax": "", "currency": "EUR", "original_amount": "", "original_currency": "", "fx_rate": "", "description": "", "transaction_id": "import-test", "counterparty_name": "", "counterparty_iban": "", "payment_reference": "", "mcc_code": "",
    }
    pd.DataFrame([row], columns=columns).to_csv(tmp_path / "movements.csv", index=False)
    movement = TradeRepublicImporter().load(tmp_path / "movements.csv")[0]
    assert movement.asset_class is None


def test_yahoo_provider_maps_stock_isins_to_tickers(monkeypatch):
    class FakeHistory:
        empty = False
        class _Close:
            class _ILoc:
                def __getitem__(self, index):
                    return 100
            iloc = _ILoc()
        def __getitem__(self, key):
            return self._Close()

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol
            self.fast_info = {"currency": "USD"}
        def history(self, **kwargs):
            return FakeHistory()

    class FakeCurrencyRates:
        def get_rate(self, source, target):
            assert (source, target) == ("USD", "EUR")
            return Decimal("0.9")

    monkeypatch.setattr(yahoo.yf, "Ticker", FakeTicker)
    prices = yahoo.YahooFinancePriceProvider(FakeCurrencyRates()).get_prices(["US55024U1097", "US1717793095"])
    assert prices == {"US55024U1097": Decimal("90.00"), "US1717793095": Decimal("90.00")}
