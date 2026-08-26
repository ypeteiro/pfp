from datetime import datetime
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
            assert kwargs["end"] == WHEN.date()
            assert kwargs["auto_adjust"] is False
            return History()

        @property
        def fast_info(self):
            return {"currency": "EUR"}

    monkeypatch.setattr("pfp.market.yahoo_historical.yf.Ticker", lambda _: Ticker())

    provider = YahooFinanceHistoricalPriceProvider()

    assert provider.price("IE00BK5BQT80", WHEN) == Decimal("123.46")


def test_yahoo_historical_price_provider_returns_none_for_unknown_symbol():
    provider = YahooFinanceHistoricalPriceProvider()

    assert provider.price("UNKNOWN", WHEN) is None
