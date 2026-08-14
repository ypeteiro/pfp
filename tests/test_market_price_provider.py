from decimal import Decimal

import pytest

from pfp.market.base import MarketPriceProvider


def test_market_price_provider_is_abstract():
    with pytest.raises(TypeError):
        MarketPriceProvider()


def test_market_price_provider_contract():
    class FakeProvider(MarketPriceProvider):

        def get_prices(
            self,
            symbols: list[str],
        ) -> dict[str, Decimal]:

            return {
                symbol: Decimal("100")
                for symbol in symbols
            }

    provider = FakeProvider()

    prices = provider.get_prices(
        ["BTC", "TEST"]
    )

    assert prices == {
        "BTC": Decimal("100"),
        "TEST": Decimal("100"),
    }