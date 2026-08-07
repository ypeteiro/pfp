import argparse
from pathlib import Path

from pfp.cli_output import print_portfolio
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter


def cmd_import_tr(csv_file: str) -> None:
    importer = TradeRepublicImporter()
    movements = importer.load(Path(csv_file))

    engine = PortfolioEngine()
    portfolio = engine.build(movements)

    print_portfolio(portfolio)


def main() -> None:
    parser = argparse.ArgumentParser(prog="pfp")

    subparsers = parser.add_subparsers(dest="command")

    import_tr = subparsers.add_parser(
        "import-tr",
        help="Importa un CSV de Trade Republic",
    )

    import_tr.add_argument("csv")

    args = parser.parse_args()

    if args.command == "import-tr":
        cmd_import_tr(args.csv)
        return

    print("PFP v0.2.0-alpha1")


if __name__ == "__main__":
    main()