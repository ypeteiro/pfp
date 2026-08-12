import argparse

from pfp.engine.history_engine import HistoryEngine
from pfp.importers.snapshot_repository import SnapshotRepository
from pfp.importers.trade_republic import TradeRepublicImporter

DEFAULT_SNAPSHOTS_FILE = "data/imports/snapshots.csv"


def run_history(snapshots_file=DEFAULT_SNAPSHOTS_FILE, movements_file=None):
    snapshots = SnapshotRepository(snapshots_file).load()
    capital_flows = []
    if movements_file is not None:
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
        "Aportado    Rentabilidad"
    )
    for point in history.points:
        print(
            f"{point.snapshot.datetime.isoformat():<27}"
            f" {point.snapshot.total_value:>12.2f} €"
            f" {point.capital_flow:>10.2f} €"
            f" {point.cumulative_capital_flow:>10.2f} €"
            f" {point.performance:>13.2f} €"
        )

    print()
    print(f"Inicial             : {history.initial_value:.2f} €")
    print(f"Actual              : {history.current_value:.2f} €")
    print(f"Capital aportado neto: {history.cumulative_capital_flow:.2f} €")
    print(f"Rentabilidad        : {history.total_performance:.2f} €")
    print(f"Rentabilidad %      : {history.total_performance_percent:.2f} %")
    print()

    if movements_file is None:
        print("Nota: ejecuta history con --movements-file para descontar aportaciones y retiradas.")
        print()

    return history


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pfp history")
    parser.add_argument("--snapshots-file", default=DEFAULT_SNAPSHOTS_FILE)
    parser.add_argument("--movements-file")
    args = parser.parse_args(argv)
    run_history(args.snapshots_file, args.movements_file)
