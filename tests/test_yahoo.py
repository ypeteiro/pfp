from pfp.domain.asset import Asset
from pfp.domain.asset_catalog import AssetCatalog
from decimal import Decimal

from pfp.market.yahoo import YahooFinancePriceProvider


def test_yahoo_price_provider_maps_vistra_isin_to_vst(monkeypatch):
    requested = []

    class CloseSeries:
        iloc = [Decimal("140.12")]

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return CloseSeries()

    class Ticker:
        def history(self, **kwargs):
            return History()

        @property
        def fast_info(self):
            return {"currency": "USD"}

    def ticker(symbol):
        requested.append(symbol)
        return Ticker()

    class CurrencyRateProvider:
        def get_rate(self, from_currency, to_currency):
            assert from_currency == "USD"
            assert to_currency == "EUR"
            return Decimal("0.9")

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", ticker)

    provider = YahooFinancePriceProvider(CurrencyRateProvider())

    assert provider.get_prices(["US92840M1027"]) == {
        "US92840M1027": Decimal("126.11")
    }
    assert requested == ["VST"]


def test_yahoo_price_provider_maps_nvidia_isin_to_nvda(monkeypatch):
    requested = []

    class CloseSeries:
        iloc = [Decimal("200")]

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return CloseSeries()

    class Ticker:
        def history(self, **kwargs):
            return History()

        @property
        def fast_info(self):
            return {"currency": "USD"}

    def ticker(symbol):
        requested.append(symbol)
        return Ticker()

    class CurrencyRateProvider:
        def get_rate(self, from_currency, to_currency):
            return Decimal("0.9")

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", ticker)
    provider = YahooFinancePriceProvider(CurrencyRateProvider())

    assert provider.get_prices(["US67066G1040"]) == {"US67066G1040": Decimal("180.00")}
    assert requested == ["NVDA"]


def test_yahoo_price_provider_uses_asset_catalog_ticker(monkeypatch):
    symbol = "TEST-ASSET-TICKER"
    AssetCatalog._assets.pop(symbol, None)
    AssetCatalog.register(
        Asset(
            symbol=symbol,
            name="Example Stock",
            portfolio_class="STOCK",
            ticker="BAC",
        )
    )
    requested = []

    class CloseSeries:
        iloc = [Decimal("100")]

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return CloseSeries()

    class Ticker:
        def history(self, **kwargs):
            return History()

        @property
        def fast_info(self):
            return {"currency": "USD"}

    def ticker(symbol):
        requested.append(symbol)
        return Ticker()

    class CurrencyRateProvider:
        def get_rate(self, from_currency, to_currency):
            return Decimal("0.9")

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", ticker)

    try:
        provider = YahooFinancePriceProvider(CurrencyRateProvider())
        assert provider.get_prices([symbol]) == {symbol: Decimal("90.00")}
        assert requested == ["BAC"]
    finally:
        AssetCatalog._assets.pop(symbol, None)


def test_yahoo_price_provider_uses_asset_isin_without_manual_mapping(monkeypatch):
    symbol = "TEST-ISIN-ASSET"
    AssetCatalog._assets.pop(symbol, None)
    AssetCatalog.register(Asset(symbol, "Example ETF", "EQUITY", isin="IE00TESTISIN"))
    requested = []

    class Search:
        def __init__(self, query, max_results):
            assert query == "IE00TESTISIN"
            assert max_results == 10
            self.quotes = [{"symbol": "VWCE.DE", "isin": "IE00TESTISIN", "longname": "Example ETF"}]

    monkeypatch.setattr("pfp.market.yahoo.yf.Search", Search)

    class CloseSeries:
        iloc = [Decimal("100")]

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return CloseSeries()

    class Ticker:
        def history(self, **kwargs):
            return History()

        @property
        def fast_info(self):
            return {"currency": "EUR"}

    def ticker(value):
        requested.append(value)
        return Ticker()

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", ticker)
    try:
        provider = YahooFinancePriceProvider()
        assert provider.get_prices([symbol]) == {symbol: Decimal("100.00")}
        assert requested == ["VWCE.DE"]
    finally:
        AssetCatalog._assets.pop(symbol, None)


def test_lookup_yahoo_asset_does_not_guess_from_unrelated_isin_result(monkeypatch):
    class Search:
        def __init__(self, query, max_results):
            assert query == "IE00TESTISIN"
            assert max_results == 10
            self.quotes = [
                {
                    "symbol": "$0P00000WLG.F",
                    "longname": "Unrelated Morningstar result",
                }
            ]

    monkeypatch.setattr("pfp.market.yahoo.yf.Search", Search)

    from pfp.market.yahoo import lookup_yahoo_asset

    assert lookup_yahoo_asset("IE00TESTISIN") is None


def test_lookup_yahoo_asset_accepts_exact_isin_result(monkeypatch):
    class Search:
        def __init__(self, query, max_results):
            self.quotes = [
                {
                    "symbol": "$0P00000WLG.F",
                    "longname": "Wrong result",
                },
                {
                    "symbol": "VWCE.DE",
                    "isin": "IE00TESTISIN",
                    "longname": "Example ETF",
                },
            ]

    monkeypatch.setattr("pfp.market.yahoo.yf.Search", Search)

    from pfp.market.yahoo import lookup_yahoo_asset

    assert lookup_yahoo_asset("IE00TESTISIN") == {
        "ticker": "VWCE.DE",
        "name": "Example ETF",
    }
