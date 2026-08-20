from decimal import Decimal

from pfp.market.yahoo import YAHOO_SYMBOLS, YahooFinancePriceProvider


def test_ccc_isin_maps_to_its_yahoo_ticker():
    assert YAHOO_SYMBOLS["US12510Q1004"] == "CCC"


def test_ccc_price_is_converted_from_usd_to_eur(monkeypatch):
    class FakeSeries:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return self

        def iloc(self):
            return self

        def __getitem__(self, key):
            return Decimal("6")

    class FakeTicker:
        fast_info = {"currency": "USD"}

        def history(self, period, auto_adjust):
            assert period == "1d"
            assert auto_adjust is False
            return FakeSeries()

    class FakeRates:
        def get_rate(self, source, target):
            assert (source, target) == ("USD", "EUR")
            return Decimal("0.9")

    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", lambda symbol: FakeTicker())

    prices = YahooFinancePriceProvider(currency_rate_provider=FakeRates()).get_prices(
        ["US12510Q1004"]
    )

    assert prices == {"US12510Q1004": Decimal("5.40")}
