import argparse
from decimal import Decimal

from pfp.cli_output import print_portfolio
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.engine.recommendation_engine import RecommendationEngine
from pfp.importers.price_importer import PriceImporter
from pfp.importers.trade_republic import TradeRepublicImporter


def build_parser():

    parser = argparse.ArgumentParser(
        prog="pfp",
        description="Personal Finance Portfolio",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    import_tr_parser = subparsers.add_parser(
        "import-tr",
        help="Import a Trade Republic CSV",
    )

    import_tr_parser.add_argument(
        "csv_file",
    )

    portfolio_parser = subparsers.add_parser(
        "portfolio",
        help="Build and value a portfolio",
    )

    portfolio_parser.add_argument(
        "movements_file",
    )

    portfolio_parser.add_argument(
        "prices_file",
    )

    recommend_parser = subparsers.add_parser(
        "recommend",
        help="Recommend where to invest a new contribution",
    )

    recommend_parser.add_argument(
        "amount",
        type=Decimal,
    )

    recommend_parser.add_argument(
        "movements_file",
    )

    return parser


def load_portfolio(movements_file):

    importer = TradeRepublicImporter()

    movements = importer.load(
        movements_file
    )

    return PortfolioEngine().build(
        movements
    )


def run_import_tr(csv_file):

    portfolio = load_portfolio(
        csv_file
    )

    print_portfolio(
        portfolio
    )


def run_portfolio(
    movements_file,
    prices_file,
):

    movement_importer = TradeRepublicImporter()
    price_importer = PriceImporter()

    movements = movement_importer.load(
        movements_file
    )

    prices = price_importer.load(
        prices_file
    )

    portfolio = PortfolioEngine().build(
        movements,
        prices,
    )

    print_portfolio(
        portfolio
    )


def run_recommend(
    amount,
    movements_file,
):

    portfolio = load_portfolio(
        movements_file
    )

    recommendation_engine = RecommendationEngine()

    recommendation = (
        recommendation_engine.recommend(
            portfolio,
            amount,
        )
    )

    print()
    print("========== RECOMENDACIÓN ==========")
    print()

    print(
        f"Aportación total : "
        f"{recommendation.total_amount:.2f} €"
    )

    print()

    for allocation in recommendation.allocations:

        if allocation.amount <= 0:
            continue

        print(
            f"{_class_label(allocation.portfolio_class):20}"
            f": {allocation.amount:>8.2f} €"
        )

        if allocation.symbol is not None:

            print(
                f"{'':20}"
                f"→ {allocation.symbol}"
                f" ({allocation.asset_name})"
            )

    print()

    total = sum(
        allocation.amount
        for allocation in recommendation.allocations
    )

    print(
        f"Total             : {total:.2f} €"
    )

    print()


def _class_label(portfolio_class):

    labels = {
        "EQUITY": "Renta variable",
        "FIXED_INCOME": "Renta fija",
        "GOLD": "Oro",
        "CRYPTO": "Crypto",
        "UNKNOWN": "Sin clasificar",
    }

    return labels.get(
        portfolio_class,
        portfolio_class,
    )


def main():

    parser = build_parser()

    args = parser.parse_args()

    if args.command == "import-tr":

        run_import_tr(
            args.csv_file
        )

    elif args.command == "portfolio":

        run_portfolio(
            args.movements_file,
            args.prices_file,
        )

    elif args.command == "recommend":

        run_recommend(
            args.amount,
            args.movements_file,
        )


if __name__ == "__main__":
    main()