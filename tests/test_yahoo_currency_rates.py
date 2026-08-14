from decimal import Decimal

import pandas as pd
import pytest

from pfp.market.yahoo_currency_rates import (
    YahooCurrencyRateProvider,
)


class FakeTicker:

    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, auto_adjust):
        return pd.DataFrame(
            {
                "Close": [1.172345678],
            }
        )


class EmptyTicker:

    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, auto_adjust):
        return pd.DataFrame()


def test_same_currency_returns_one():

    provider = YahooCurrencyRateProvider()

    assert provider.get_rate(
        "EUR",
        "EUR",
    ) == Decimal("1")


def test_yahoo_currency_provider_returns_rate(
    monkeypatch,
):

    monkeypatch.setattr(
        "pfp.market.yahoo_currency_rates.yf.Ticker",
        FakeTicker,
    )

    provider = YahooCurrencyRateProvider()

    rate = provider.get_rate(
        "GBP",
        "EUR",
    )

    assert rate == Decimal("1.172346")


def test_yahoo_currency_provider_ignores_empty_history(
    monkeypatch,
):

    monkeypatch.setattr(
        "pfp.market.yahoo_currency_rates.yf.Ticker",
        EmptyTicker,
    )

    provider = YahooCurrencyRateProvider()

    with pytest.raises(
        ValueError,
        match="No currency rate available",
    ):
        provider.get_rate(
            "GBP",
            "EUR",
        )


def test_yahoo_currency_provider_rejects_unknown_pair():

    provider = YahooCurrencyRateProvider()

    with pytest.raises(
        ValueError,
        match="Unsupported currency pair",
    ):
        provider.get_rate(
            "JPY",
            "EUR",
        )