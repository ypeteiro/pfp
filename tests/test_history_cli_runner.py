from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import replace

from pfp.domain.capital_flow import CapitalFlow, FlowType
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

    monkeypatch.setattr("pfp.history_cli._capture_current_snapshot", lambda *args: None)

    history = run_history(snapshots_file, movements_file)
    output = capsys.readouterr().out

    assert history.points == ()
    assert "HISTÓRICO" in output


def test_history_reports_multi_period_twr_and_xirr(tmp_path, monkeypatch, capsys):
    snapshots_file = tmp_path / "snapshots.csv"
    movements_file = tmp_path / "movements.csv"
    repository = SnapshotRepository(snapshots_file)
    first = replace(_snapshot(10, "10000"), datetime=datetime(2025, 8, 10, tzinfo=timezone.utc))
    second = _snapshot(11, "10500")
    repository.save(first)
    repository.save(second)

    monkeypatch.setattr("pfp.history_cli._capture_current_snapshot", lambda *args: None)
    monkeypatch.setattr(
        "pfp.history_cli.TradeRepublicImporter.load_capital_flows",
        lambda self, path: [
            CapitalFlow(
                datetime=datetime(2025, 8, 10, 12, tzinfo=timezone.utc),
                amount=Decimal("500"),
                flow_type=FlowType.CONTRIBUTION,
            )
        ],
    )

    history = run_history(snapshots_file, movements_file)
    output = capsys.readouterr().out

    assert len(history.points) == 2
    assert history.points[0].time_weighted_return is None
    assert history.points[1].time_weighted_return == Decimal("0")
    assert history.time_weighted_return == Decimal("0")
    assert history.xirr is not None
    assert "Rentabilidad TWR" in output
    assert "Rentabilidad XIRR" in output
