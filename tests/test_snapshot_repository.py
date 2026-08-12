from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.snapshot import PortfolioSnapshot
from pfp.importers.snapshot_repository import SnapshotRepository


def _snapshot():
    return PortfolioSnapshot(
        datetime=datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc),
        total_value=Decimal("24859.21"),
        cash=Decimal("3303.39"),
        invested_cost=Decimal("21696.61"),
        market_value=Decimal("21555.82"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("-140.79"),
        equity_value=Decimal("16000"),
        fixed_income_value=Decimal("4000"),
        gold_value=Decimal("1000"),
        crypto_value=Decimal("98.99"),
    )


def test_save_and_load_snapshot(tmp_path):
    path = tmp_path / "snapshots.csv"
    repository = SnapshotRepository(path)
    snapshot = _snapshot()

    repository.save(snapshot)

    assert repository.load() == [snapshot]


def test_save_creates_parent_directory(tmp_path):
    path = tmp_path / "data" / "snapshots.csv"
    SnapshotRepository(path).save(_snapshot())

    assert path.exists()


def test_load_missing_file_returns_empty_list(tmp_path):
    assert SnapshotRepository(tmp_path / "missing.csv").load() == []


def test_save_multiple_snapshots(tmp_path):
    path = tmp_path / "snapshots.csv"
    repository = SnapshotRepository(path)
    first = _snapshot()
    second = PortfolioSnapshot(
        **{**first.__dict__, "datetime": datetime(2026, 8, 13, tzinfo=timezone.utc), "total_value": Decimal("25000")}
    )

    repository.save(first)
    repository.save(second)

    assert repository.load() == [first, second]
