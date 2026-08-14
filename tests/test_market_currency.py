from decimal import Decimal

import pytest

from pfp.market.currency import normalize_price


def test_normalize_gbp_pence():

    assert normalize_price(
        Decimal("6234.887"),
        "GBp",
    ) == Decimal("62.34887")


def test_eur_price_is_unchanged():

    assert normalize_price(
        Decimal("168.46"),
        "EUR",
    ) == Decimal("168.46")


def test_gbp_price_is_unchanged():

    assert normalize_price(
        Decimal("62.34"),
        "GBP",
    ) == Decimal("62.34")


def test_usd_price_is_unchanged():

    assert normalize_price(
        Decimal("100"),
        "USD",
    ) == Decimal("100")


def test_unknown_currency_raises():

    with pytest.raises(
        ValueError,
        match="Unsupported market currency",
    ):
        normalize_price(
            Decimal("100"),
            "JPY",
        )