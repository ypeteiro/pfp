from decimal import Decimal

import pytest

from pfp.market.currency_rates import CurrencyRateProvider


def test_currency_rate_provider_is_abstract():

    with pytest.raises(TypeError):
        CurrencyRateProvider()


def test_currency_rate_provider_contract():

    class FakeCurrencyRateProvider(
        CurrencyRateProvider
    ):

        def get_rate(
            self,
            from_currency: str,
            to_currency: str,
        ) -> Decimal:

            return Decimal("1.15")

    provider = FakeCurrencyRateProvider()

    rate = provider.get_rate(
        "GBP",
        "EUR",
    )

    assert rate == Decimal("1.15")
