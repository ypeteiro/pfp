from decimal import Decimal

import pytest

from pfp.market.vanguard import (
    VanguardApiPriceProvider,
    VanguardPriceProvider,
)


def test_vanguard_price_provider_is_abstract():

    with pytest.raises(TypeError):
        VanguardPriceProvider()


def test_vanguard_price_provider_contract():

    class FakeVanguardPriceProvider(
        VanguardPriceProvider
    ):

        def get_prices(
            self,
            symbols: list[str],
        ) -> dict[str, Decimal]:

            return {
                "IE00B03HD191": Decimal("62.50")
            }

    provider = FakeVanguardPriceProvider()

    prices = provider.get_prices(
        ["IE00B03HD191"]
    )

    assert prices == {
        "IE00B03HD191": Decimal("62.50")
    }


def test_vanguard_api_provider_ignores_unknown_symbols():

    provider = VanguardApiPriceProvider()

    prices = provider.get_prices(
        ["UNKNOWN"]
    )

    assert prices == {}


def test_vanguard_api_provider_parses_eur_nav(
    monkeypatch,
):

    class FakeResponse:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):

            return (
                b"""
                <html>
                    <div>
                        NAV Price (EUR)
                    </div>
                    <span>EUR 64.0925</span>
                </html>
                """
            )

    def fake_urlopen(
        request,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "pfp.market.vanguard.urlopen",
        fake_urlopen,
    )

    provider = VanguardApiPriceProvider()

    prices = provider.get_prices(
        ["IE00B03HD191"]
    )

    assert prices == {
        "IE00B03HD191": Decimal("64.09")
    }


def test_vanguard_api_provider_parses_json_nav(
    monkeypatch,
):

    class FakeResponse:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):

            return (
                b"""
                {
                    "navPrice": 64.0925
                }
                """
            )

    def fake_urlopen(
        request,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "pfp.market.vanguard.urlopen",
        fake_urlopen,
    )

    provider = VanguardApiPriceProvider()

    prices = provider.get_prices(
        ["IE00B03HD191"]
    )

    assert prices == {
        "IE00B03HD191": Decimal("64.09")
    }


def test_vanguard_api_provider_handles_missing_nav(
    monkeypatch,
):

    class FakeResponse:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return b"<html>No NAV</html>"

    def fake_urlopen(
        request,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "pfp.market.vanguard.urlopen",
        fake_urlopen,
    )

    provider = VanguardApiPriceProvider()

    prices = provider.get_prices(
        ["IE00B03HD191"]
    )

    assert prices == {}


def test_vanguard_api_provider_handles_network_error(
    monkeypatch,
):

    def fake_urlopen(
        request,
        timeout,
    ):
        raise OSError("network error")

    monkeypatch.setattr(
        "pfp.market.vanguard.urlopen",
        fake_urlopen,
    )

    provider = VanguardApiPriceProvider()

    prices = provider.get_prices(
        ["IE00B03HD191"]
    )

    assert prices == {}