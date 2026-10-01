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
