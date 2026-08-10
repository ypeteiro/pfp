import argparse
from decimal import Decimal

from pfp.cli_output import print_portfolio
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.engine.recommendation_engine import (
    RecommendationEngine,
)
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import (
    CompositePriceProvider,
)


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


def run_portfolio(movements_file):

    importer = TradeRepublicImporter()
    price_provider = CompositePriceProvider()
    portfolio_engine = PortfolioEngine()

    movements = importer.load(
        movements_file
    )

    portfolio = portfolio_engine.build(
        movements
    )

    symbols = list(
        portfolio.positions.keys()
    )

    prices = price_provider.get_prices(
        symbols
    )

    portfolio = portfolio_engine.build(
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

    recommendation_engine = (
        RecommendationEngine()
    )

    recommendation = (
        recommendation_engine.recommend(
            portfolio,
            amount,
        )
    )

    print()
    print(
        "========== ORDEN DE INVERSIÓN =========="
    )
    print()

    print(
        f"Aportación total : "
        f"{recommendation.total_amount:.2f} €"
    )
    print()

    for order in recommendation.orders:

        print(
            f"  {order.amount:.2f} € "
            f"→ {order.symbol} "
            f"({order.asset_name})"
        )

    print()

    print(
        f"TOTAL             : "
        f"{recommendation.total_amount:.2f} €"
    )
    print()


def main():

    parser = build_parser()

    args = parser.parse_args()

    if args.command == "import-tr":

        run_import_tr(
            args.csv_file
        )

    elif args.command == "portfolio":

        run_portfolio(
            args.movements_file
        )

    elif args.command == "recommend":

        run_recommend(
            args.amount,
            args.movements_file,
        )


if __name__ == "__main__":
    main()
