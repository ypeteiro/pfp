import pytest

from pfp.domain.asset import Asset


def test_asset_rejects_empty_symbol():
    with pytest.raises(ValueError, match="symbol"):
        Asset(symbol="", name="Bitcoin", portfolio_class="CRYPTO")


def test_asset_rejects_empty_name():
    with pytest.raises(ValueError, match="name"):
        Asset(symbol="BTC", name="", portfolio_class="CRYPTO")


def test_asset_rejects_empty_portfolio_class():
    with pytest.raises(ValueError, match="portfolio_class"):
        Asset(symbol="BTC", name="Bitcoin", portfolio_class="")
