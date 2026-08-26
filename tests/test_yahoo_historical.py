from datetime import datetime, timedelta
from decimal import Decimal

from pfp.market.yahoo_historical import YahooFinanceHistoricalPriceProvider


WHEN = datetime(2026, 1, 15, 10)


def test_yahoo_historical_price_provider_returns_eur_close(monkeypatch):
    class Series:
        class _ILoc:
            def __getitem__(self, index):
                assert index == 0
                return Decimal("123.456")

        @property
        def iloc(self):
            return self._ILoc()

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return Series()

    class Ticker:
        def history(self, **kwargs):
            assert kwargs["start"] == WHEN.date()
            assert kwargs["end"] == WHEN.date() + timedelta(days=1)
            assert kwargs["auto_adjust"] is False
            return History()

        @property
        def fast_info(self):
            return {"currency": "EUR"}

    monkeypatch.setattr("pfp.market.yahoo_historical.yf.Ticker", lambda _: Ticker())

    provider = YahooFinanceHistoricalPriceProvider()

    assert provider.price("IE00BK5BQT80", WHEN) == Decimal("123.46")


def test_yahoo_historical_price_provider_converts_usd_with_historical_rate(monkeypatch):
    class Series:
        class _ILoc:
            def __getitem__(self, index):
                assert index == 0
                return Decimal("100")

        @property
        def iloc(self):
            return self._ILoc()

    class History:
        empty = False

        def __getitem__(self, key):
            assert key == "Close"
            return Series()

    class Ticker:
        def history(self, **kwargs):
            assert kwargs["start"] == WHEN.date()
            assert kwargs["end"] == WHEN.date() + timedelta(days=1)
            assert kwargs["auto_adjust"] is False
            return History()

        @property
        def fast_info(self):
            return {"currency": "USD"}

    class HistoricalRateProvider:
        def get_rate_at(self, from_currency, to_currency, at):
            assert from_currency == "USD"
            assert to_currency == "EUR"
            assert at == WHEN.date()
            return Decimal("0.9")

    monkeypatch.setattr("pfp.market.yahoo_historical.yf.Ticker", lambda _: Ticker())

    provider = YahooFinanceHistoricalPriceProvider(HistoricalRateProvider())

    assert provider.price("IE00BKM4GZ66", WHEN) == Decimal("90.00")


def test_yahoo_historical_price_provider_returns_none_for_unknown_symbol():
    provider = YahooFinanceHistoricalPriceProvider()

    assert provider.price("UNKNOWN", WHEN) is None
