from decimal import Decimal

import pandas as pd

from pfp.market.yahoo import YahooFinancePriceProvider


class FakeFastInfo:

    def get(self, key):
        if key == "currency":
            return "EUR"

        return None


class FakeTicker:

    def __init__(self, symbol):
        self.symbol = symbol
        self.fast_info = FakeFastInfo()

    def history(self, period, auto_adjust):
        return pd.DataFrame(
            {
                "Close": [100.25],
            }
        )


class EmptyTicker:

    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, auto_adjust):
        return pd.DataFrame()


class DecimalFastInfo:

    def get(self, key):
        if key == "currency":
            return "EUR"

        return None


class DecimalTicker:

    def __init__(self, symbol):
        self.symbol = symbol
        self.fast_info = DecimalFastInfo()

    def history(self, period, auto_adjust):
        return pd.DataFrame(
            {
                "Close": [56236.9609375],
            }
        )


def test_yahoo_provider_returns_prices(monkeypatch):

    monkeypatch.setattr(
        "pfp.market.yahoo.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinancePriceProvider()

    prices = provider.get_prices(
        ["BTC"]
    )

    assert prices == {
        "BTC": Decimal("100.25")
    }


def test_yahoo_provider_ignores_unknown_symbols(
    monkeypatch,
):

    monkeypatch.setattr(
        "pfp.market.yahoo.yf.Ticker",
        FakeTicker,
    )

    provider = YahooFinancePriceProvider()

    prices = provider.get_prices(
        ["UNKNOWN"]
    )

    assert prices == {}


def test_yahoo_provider_ignores_missing_price(
    monkeypatch,
):

    monkeypatch.setattr(
        "pfp.market.yahoo.yf.Ticker",
        EmptyTicker,
    )

    provider = YahooFinancePriceProvider()

    prices = provider.get_prices(
        ["BTC"]
    )

    assert prices == {}


def test_yahoo_provider_rounds_price(
    monkeypatch,
):

    monkeypatch.setattr(
        "pfp.market.yahoo.yf.Ticker",
        DecimalTicker,
    )

    provider = YahooFinancePriceProvider()

    prices = provider.get_prices(
        ["BTC"]
    )

    assert prices["BTC"] == Decimal(
        "56236.96"
    )
