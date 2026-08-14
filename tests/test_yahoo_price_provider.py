from decimal import Decimal

import pandas as pd

from pfp.market.yahoo import YahooFinancePriceProvider


class FakeFastInfo:

    def __init__(self, currency="EUR"):
        self.currency = currency

    def get(self, key):
        if key == "currency":
            return self.currency
        return None


class FakeTicker:

    def __init__(self, symbol):
        self.symbol = symbol
        self.fast_info = FakeFastInfo()

    def history(self, period, auto_adjust):
        return pd.DataFrame({"Close": [100.25]})


class EmptyTicker:

    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period, auto_adjust):
        return pd.DataFrame()


class DecimalTicker:

    def __init__(self, symbol):
        self.symbol = symbol
        self.fast_info = FakeFastInfo()

    def history(self, period, auto_adjust):
        return pd.DataFrame({"Close": [56236.9609375]})


class CurrencyTicker:

    CURRENCIES = {
        "VWCE.DE": "USD",
        "SGLN.L": "GBp",
        "EUNL.DE": "EUR",
    }

    def __init__(self, symbol):
        self.symbol = symbol
        self.fast_info = FakeFastInfo(self.CURRENCIES[symbol])

    def history(self, period, auto_adjust):
        return pd.DataFrame({"Close": [100]})


class FakeCurrencyRateProvider:

    RATES = {
        ("USD", "EUR"): Decimal("0.80"),
        ("GBP", "EUR"): Decimal("1.20"),
    }

    def get_rate(self, from_currency, to_currency):
        return self.RATES[(from_currency, to_currency)]


class FailingCurrencyRateProvider:

    def get_rate(self, from_currency, to_currency):
        raise RuntimeError("FX unavailable")


def test_yahoo_provider_returns_prices(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", FakeTicker)

    provider = YahooFinancePriceProvider()
    prices = provider.get_prices(["BTC"])

    assert prices == {"BTC": Decimal("100.25")}


def test_yahoo_provider_ignores_unknown_symbols(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", FakeTicker)

    provider = YahooFinancePriceProvider()
    prices = provider.get_prices(["UNKNOWN"])

    assert prices == {}


def test_yahoo_provider_ignores_missing_price(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", EmptyTicker)

    provider = YahooFinancePriceProvider()
    prices = provider.get_prices(["BTC"])

    assert prices == {}


def test_yahoo_provider_rounds_price(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", DecimalTicker)

    provider = YahooFinancePriceProvider()
    prices = provider.get_prices(["BTC"])

    assert prices["BTC"] == Decimal("56236.96")


def test_yahoo_provider_converts_usd_to_eur(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", CurrencyTicker)

    provider = YahooFinancePriceProvider(
        currency_rate_provider=FakeCurrencyRateProvider()
    )

    prices = provider.get_prices(["IE00BK5BQT80"])

    assert prices == {"IE00BK5BQT80": Decimal("80.00")}


def test_yahoo_provider_converts_gbp_to_eur_and_normalizes_gbp_units(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", CurrencyTicker)

    provider = YahooFinancePriceProvider(
        currency_rate_provider=FakeCurrencyRateProvider()
    )

    prices = provider.get_prices(["IE00B4ND3602"])

    # 100 GBp = 1 GBP, then GBP/EUR = 1.20.
    assert prices == {"IE00B4ND3602": Decimal("1.20")}


def test_yahoo_provider_keeps_eur_price_without_fx(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", CurrencyTicker)

    provider = YahooFinancePriceProvider(
        currency_rate_provider=FailingCurrencyRateProvider()
    )

    prices = provider.get_prices(["IE00B4L5Y983"])

    assert prices == {"IE00B4L5Y983": Decimal("100.00")}


def test_yahoo_provider_skips_only_symbol_when_fx_fails(monkeypatch):
    monkeypatch.setattr("pfp.market.yahoo.yf.Ticker", CurrencyTicker)

    provider = YahooFinancePriceProvider(
        currency_rate_provider=FailingCurrencyRateProvider()
    )

    prices = provider.get_prices(["IE00BK5BQT80", "IE00B4L5Y983"])

    assert prices == {"IE00B4L5Y983": Decimal("100.00")}
