from pfp.domain.asset import Asset
from pfp.domain.asset_catalog import AssetCatalog


def test_catalog_can_register_a_new_asset_without_code_changes():
    symbol = "TEST-NEW-ASSET"
    asset = Asset(symbol, "New Asset", "STOCK", ticker="NEW")

    try:
        AssetCatalog.register(asset)
        assert AssetCatalog.get(symbol) == asset
        assert asset in AssetCatalog.all()
    finally:
        AssetCatalog._assets.pop(symbol, None)
