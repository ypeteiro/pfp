from pfp.domain.asset import Asset
from pfp.importers.asset_repository import AssetRepository


def test_asset_repository_round_trip(tmp_path):
    repository = AssetRepository(tmp_path / "assets.csv")
    asset = Asset(
        symbol="US1234567890",
        name="Example Holdings",
        portfolio_class="STOCK",
        isin="US1234567890",
        ticker="EXMP",
    )

    repository.save(asset)

    assert repository.load() == [asset]


def test_asset_repository_updates_existing_symbol(tmp_path):
    repository = AssetRepository(tmp_path / "assets.csv")
    first = Asset("TEST", "Test", "STOCK", ticker="TST")
    updated = Asset("TEST", "Updated Test", "STOCK", ticker="TST2")

    repository.save(first)
    repository.save(updated)

    assert repository.load() == [updated]
