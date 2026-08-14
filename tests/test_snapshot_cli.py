from decimal import Decimal
from pathlib import Path

from pfp.cli import load_portfolio, run_snapshot
from pfp.importers.snapshot_repository import SnapshotRepository


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


class StubPriceProvider:
    def get_prices(self, symbols):
        return {symbol: Decimal("100") for symbol in symbols}


def test_run_snapshot_persists_current_state(tmp_path, capsys):
    snapshots_file = tmp_path / "snapshots.csv"

    run_snapshot(
        MOVEMENTS_FILE,
        snapshots_file=snapshots_file,
        investments_file=tmp_path / "investments.csv",
        sales_file=tmp_path / "sales.csv",
        price_provider=StubPriceProvider(),
    )

    snapshots = SnapshotRepository(snapshots_file).load()
    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.total_value == snapshot.cash + snapshot.market_value
    assert snapshot.market_value >= Decimal("0")
    assert snapshot.datetime.tzinfo is not None
    assert "SNAPSHOT" in capsys.readouterr().out


def test_run_snapshot_captures_asset_classes(tmp_path):
    snapshots_file = tmp_path / "snapshots.csv"

    run_snapshot(
        MOVEMENTS_FILE,
        snapshots_file=snapshots_file,
        investments_file=tmp_path / "investments.csv",
        sales_file=tmp_path / "sales.csv",
        price_provider=StubPriceProvider(),
    )

    snapshot = SnapshotRepository(snapshots_file).load()[0]
    assert snapshot.equity_value > 0
    assert snapshot.fixed_income_value > 0
    assert snapshot.gold_value > 0
    assert snapshot.crypto_value > 0


def test_run_snapshot_appends_history(tmp_path):
    snapshots_file = tmp_path / "snapshots.csv"
    kwargs = dict(
        snapshots_file=snapshots_file,
        investments_file=tmp_path / "investments.csv",
        sales_file=tmp_path / "sales.csv",
        price_provider=StubPriceProvider(),
    )

    run_snapshot(MOVEMENTS_FILE, **kwargs)
    run_snapshot(MOVEMENTS_FILE, **kwargs)

    snapshots = SnapshotRepository(snapshots_file).load()
    assert len(snapshots) == 2
    assert snapshots[0].datetime <= snapshots[1].datetime


def test_snapshot_values_match_portfolio_market_value(tmp_path):
    snapshots_file = tmp_path / "snapshots.csv"
    portfolio = load_portfolio(
        MOVEMENTS_FILE,
        tmp_path / "investments.csv",
        tmp_path / "sales.csv",
    )
    expected_market_value = sum(
        position.shares * Decimal("100")
        for position in portfolio.positions.values()
    )

    run_snapshot(
        MOVEMENTS_FILE,
        snapshots_file=snapshots_file,
        investments_file=tmp_path / "investments.csv",
        sales_file=tmp_path / "sales.csv",
        price_provider=StubPriceProvider(),
    )

    snapshot = SnapshotRepository(snapshots_file).load()[0]
    assert snapshot.market_value == expected_market_value
