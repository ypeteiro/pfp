from decimal import Decimal

from pfp.market.price_provider import CompositePriceProvider


class FakeYahooProvider:
    def __init__(self, prices):
        self.prices = prices

    def get_prices(self, symbols):
        return {symbol: self.prices[symbol] for symbol in symbols if symbol in self.prices}


class FakeVanguardProvider:
    def __init__(self, prices):
        self.prices = prices
        self.requested_symbols = []

    def get_prices(self, symbols):
        self.requested_symbols.extend(symbols)
        return {symbol: self.prices[symbol] for symbol in symbols if symbol in self.prices}


class FailingProvider:
    def get_prices(self, symbols):
        raise RuntimeError("provider unavailable")


def test_composite_provider_uses_yahoo_prices():
    yahoo = FakeYahooProvider({"BTC": Decimal("56200.00")})
    vanguard = FakeVanguardProvider({"IE00B03HD191": Decimal("62.35")})
    provider = CompositePriceProvider(yahoo_provider=yahoo, vanguard_provider=vanguard)

    prices = provider.get_prices(["BTC"])

    assert prices == {"BTC": Decimal("56200.00")}
    assert vanguard.requested_symbols == []


def test_composite_provider_uses_vanguard_for_missing_prices():
    yahoo = FakeYahooProvider({"BTC": Decimal("56200.00")})
    vanguard = FakeVanguardProvider({"IE00B03HD191": Decimal("62.35")})
    provider = CompositePriceProvider(yahoo_provider=yahoo, vanguard_provider=vanguard)

    prices = provider.get_prices(["BTC", "IE00B03HD191"])

    assert prices == {"BTC": Decimal("56200.00"), "IE00B03HD191": Decimal("62.35")}
    assert vanguard.requested_symbols == ["IE00B03HD191"]


def test_composite_provider_keeps_unavailable_prices_missing():
    yahoo = FakeYahooProvider({})
    vanguard = FakeVanguardProvider({})
    provider = CompositePriceProvider(yahoo_provider=yahoo, vanguard_provider=vanguard)

    prices = provider.get_prices(["IE00B03HD191", "UNKNOWN"])

    assert prices == {}
    assert vanguard.requested_symbols == ["IE00B03HD191", "UNKNOWN"]


def test_composite_provider_falls_back_when_yahoo_fails():
    vanguard = FakeVanguardProvider({"IE00B03HD191": Decimal("62.35")})
    provider = CompositePriceProvider(yahoo_provider=FailingProvider(), vanguard_provider=vanguard)

    prices = provider.get_prices(["IE00B03HD191"])

    assert prices == {"IE00B03HD191": Decimal("62.35")}
    assert vanguard.requested_symbols == ["IE00B03HD191"]


def test_composite_provider_returns_empty_when_all_providers_fail():
    provider = CompositePriceProvider(
        yahoo_provider=FailingProvider(),
        vanguard_provider=FailingProvider(),
    )

    assert provider.get_prices(["IE00B03HD191"]) == {}
