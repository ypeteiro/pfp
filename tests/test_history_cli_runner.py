from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.snapshot import PortfolioSnapshot
from pfp.history_cli import run_history
from pfp.importers.snapshot_repository import SnapshotRepository


def _snapshot(day, value):
    value = Decimal(str(value))
    return PortfolioSnapshot(
        datetime=datetime(2026, 8, day, tzinfo=timezone.utc),
        total_value=value,
        cash=Decimal("0"),
        invested_cost=Decimal("0"),
        market_value=value,
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=value,
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
    )


def test_history_captures_snapshot_when_movements_file_is_provided(tmp_path, monkeypatch, capsys):
    snapshots_file = tmp_path / "snapshots.csv"
    movements_file = tmp_path / "movements.csv"
    snapshots_file.parent.mkdir(parents=True, exist_ok=True)
    SnapshotRepository(snapshots_file).save(_snapshot(10, "20000"))

    calls = []

    def fake_capture(movements, snapshots, investments, sales):
        calls.append((movements, snapshots, investments, sales))
        SnapshotRepository(snapshots).save(_snapshot(11, "20500"))

    monkeypatch.setattr("pfp.history_cli._capture_current_snapshot", fake_capture)
    monkeypatch.setattr("pfp.history_cli.TradeRepublicImporter.load_capital_flows", lambda self, path: [])

    history = run_history(snapshots_file, movements_file)

    assert calls == [
        (
            movements_file,
            snapshots_file,
            "data/imports/investments.csv",
            "data/imports/sales.csv",
        )
    ]
    assert len(history.points) == 2
    assert history.current_value == Decimal("20500")
    assert "HISTÓRICO" in capsys.readouterr().out


def test_history_does_not_capture_without_movements_file(tmp_path, monkeypatch):
    snapshots_file = tmp_path / "snapshots.csv"
    SnapshotRepository(snapshots_file).save(_snapshot(10, "20000"))

    def fail_capture(*args):
        raise AssertionError("snapshot capture should not run")

    monkeypatch.setattr("pfp.history_cli._capture_current_snapshot", fail_capture)

    history = run_history(snapshots_file)

    assert len(history.points) == 1
    assert history.current_value == Decimal("20000")