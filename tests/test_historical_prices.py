from datetime import datetime
from decimal import Decimal

from pfp.reporting.historical_prices import MappingHistoricalPriceProvider


WHEN = datetime(2026, 1, 2, 10)


def test_mapping_historical_price_provider_returns_price_for_exact_date():
    provider = MappingHistoricalPriceProvider({WHEN: {"VWCE": Decimal("123.45")}})

    assert provider.price("VWCE", WHEN) == Decimal("123.45")


def test_mapping_historical_price_provider_returns_none_when_price_is_missing():
    provider = MappingHistoricalPriceProvider({WHEN: {"VWCE": Decimal("123.45")}})

    assert provider.price("VWCE", datetime(2026, 1, 3, 10)) is None
    assert provider.price("IWDA", WHEN) is None
