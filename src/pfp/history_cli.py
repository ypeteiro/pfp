import argparse
import io
from contextlib import redirect_stdout
from pathlib import Path

from pfp.cli import run_snapshot
from pfp.engine.history_engine import HistoryEngine
from pfp.importers.snapshot_repository import SnapshotRepository
from pfp.importers.trade_republic import TradeRepublicImporter

DEFAULT_SNAPSHOTS_FILE = "data/imports/snapshots.csv"
DEFAULT_MOVEMENTS_FILE = "data/imports/trade_republic.csv"
DEFAULT_INVESTMENTS_FILE = "data/imports/investments.csv"
DEFAULT_SALES_FILE = "data/imports/sales.csv"


def _capture_current_snapshot(movements_file, snapshots_file, investments_file, sales_file):
    with redirect_stdout(io.StringIO()):
        run_snapshot(
            movements_file,
            snapshots_file=snapshots_file,
            investments_file=investments_file,
            sales_file=sales_file,
        )


def run_history(
    snapshots_file=DEFAULT_SNAPSHOTS_FILE,
    movements_file=None,
    investments_file=DEFAULT_INVESTMENTS_FILE,
    sales_file=DEFAULT_SALES_FILE,
):
    if movements_file is not None:
        _capture_current_snapshot(
            movements_file,
            snapshots_file,
            investments_file,
            sales_file,
        )

    snapshots = SnapshotRepository(snapshots_file).load()
    capital_flows = []
    if movements_file is not None and Path(movements_file).exists():
        capital_flows = TradeRepublicImporter().load_capital_flows(movements_file)

    history = HistoryEngine().build(snapshots, capital_flows)

    print()
    print("========== HISTÓRICO ==========")
    print()

    if not history.points:
        print("No hay snapshots registrados.")
        print()
        return history

    print(
        "Fecha                      Patrimonio       Flujo       "
        "Aportado    Rentabilidad      TWR"
    )
    for point in history.points:
        twr = "N/D" if point.time_weighted_return is None else f"{point.time_weighted_return * 100:.2f} %"
        print(
            f"{point.snapshot.datetime.isoformat():<27}"
            f" {point.snapshot.total_value:>12.2f} €"
            f" {point.capital_flow:>10.2f} €"
            f" {point.cumulative_capital_flow:>10.2f} €"
            f" {point.performance:>13.2f} €"
            f" {twr:>10}"
        )

    print()
    print(f"Inicial             : {history.initial_value:.2f} €")
    print(f"Actual              : {history.current_value:.2f} €")
    print(f"Capital aportado neto: {history.cumulative_capital_flow:.2f} €")
    print(f"Rentabilidad        : {history.total_performance:.2f} €")
    print(f"Rentabilidad %      : {history.total_performance_percent:.2f} %")

    twr_percent = history.time_weighted_return_percent
    if twr_percent is None:
        print("Rentabilidad TWR    : N/D (se necesitan al menos 2 snapshots)")
    else:
        print(f"Rentabilidad TWR    : {twr_percent:.2f} %")

    xirr_percent = history.xirr_percent
    if xirr_percent is None:
        print("Rentabilidad XIRR   : N/D")
    else:
        print(f"Rentabilidad XIRR   : {xirr_percent:.2f} %")
    print()

    if movements_file is None:
        print("Nota: ejecuta history con --movements-file para descontar aportaciones y retiradas.")
        print()

    return history


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pfp history")
    parser.add_argument("--snapshots-file", default=DEFAULT_SNAPSHOTS_FILE)
    parser.add_argument("--movements-file", default=None)
    parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    args = parser.parse_args(argv)
    run_history(
        args.snapshots_file,
        args.movements_file,
        args.investments_file,
        args.sales_file,
    )
