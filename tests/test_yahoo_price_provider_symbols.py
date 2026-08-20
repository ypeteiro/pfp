from decimal import Decimal

from pfp.market.yahoo import YAHOO_SYMBOLS, YahooFinancePriceProvider


def test_ccc_isin_maps_to_its_yahoo_ticker():
    assert YAHOO_SYMBOLS["US12510Q1004"] == "CCC"


def test_ccc_price_is_converted_from_usd_to_eur(monkeypatch):
    class FakeCloseSeries:
        def __init__(self):
            self.iloc = self

        def __getitem__(self, index):
            assert index == -1
            return Decimal("6")

    class FakeHistory:
        empty = False

        def __init__(self):
            self.close = FakeCloseSeries()

        def __getitem__(self, key):
            assert key == "Close"
            return self.close

    class FakeTicker:
        fast_info = {"currency": "USD"}

        def history(self, period, auto_adjust):
            assert period == "1d"
            assert auto_adjust is False
            return FakeHistory()

    class FakeRates:
        def get_rate(self, source, target):
            assert (source, target) == ("USD", "EUR")
            return Decimal("0.9")

    def fake_ticker(symbol):
        assert symbol == "CCC"
        return FakeTicker()

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", fake_ticker)

    prices = YahooFinancePriceProvider(currency_rate_provider=FakeRates()).get_prices(
        ["US12510Q1004"]
    )

    assert prices == {"US12510Q1004": Decimal("5.40")}
