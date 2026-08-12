import argparse
from decimal import Decimal

from pfp.engine.history_engine import HistoryEngine
from pfp.importers.snapshot_repository import SnapshotRepository

DEFAULT_SNAPSHOTS_FILE = "data/imports/snapshots.csv"


def run_history(snapshots_file=DEFAULT_SNAPSHOTS_FILE):
    history = HistoryEngine().build(SnapshotRepository(snapshots_file).load())

    print()
    print("========== HISTÓRICO ==========")
    print()

    if not history.points:
        print("No hay snapshots registrados.")
        print()
        return history

    print("Fecha                      Patrimonio       Variación      Variación %")
    for point in history.points:
        print(
            f"{point.snapshot.datetime.isoformat():<27}"
            f" {point.snapshot.total_value:>12.2f} €"
            f" {point.change:>12.2f} €"
            f" {point.change_percent:>11.2f} %"
        )

    print()
    print(f"Inicial          : {history.initial_value:.2f} €")
    print(f"Actual           : {history.current_value:.2f} €")
    print(f"Variación total  : {history.total_change:.2f} €")
    print(f"Variación total %: {history.total_change_percent:.2f} %")
    print()
    print("Nota: la variación patrimonial todavía no descuenta aportaciones.")
    print("La rentabilidad real se calculará cuando integremos los flujos de capital.")
    print()

    return history


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pfp history")
    parser.add_argument("--snapshots-file", default=DEFAULT_SNAPSHOTS_FILE)
    args = parser.parse_args(argv)
    run_history(args.snapshots_file)
