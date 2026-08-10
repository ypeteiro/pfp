import argparse
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from pfp.cli_output import print_portfolio
from pfp.engine.investment_engine import InvestmentEngine
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.engine.recommendation_engine import (
    RecommendationEngine,
)
from pfp.importers.investment_repository import (
    InvestmentRepository,
)
from pfp.importers.trade_republic import (
    TradeRepublicImporter,
)
from pfp.market.price_provider import (
    CompositePriceProvider,
)


DEFAULT_INVESTMENTS_FILE = (
    "data/imports/investments.csv"
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

    invest_parser = subparsers.add_parser(
        "invest",
        help="Register an executed investment",
    )

    invest_parser.add_argument(
        "symbol",
    )

    invest_parser.add_argument(
        "shares",
        type=Decimal,
    )

    invest_parser.add_argument(
        "amount",
        type=Decimal,
    )

    invest_parser.add_argument(
        "portfolio_class",
    )

    invest_parser.add_argument(
        "movements_file",
    )

    invest_parser.add_argument(
        "--investments-file",
        default=DEFAULT_INVESTMENTS_FILE,
    )

    return parser


def load_portfolio(
    movements_file,
    investments_file=None,
):

    importer = TradeRepublicImporter()

    movements = importer.load(
        movements_file
    )

    investments = None

    if investments_file is not None:

        repository = InvestmentRepository(
            investments_file
        )

        investments = repository.load()

    return PortfolioEngine().build(
        movements,
        investments=investments,
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

    investments_repository = InvestmentRepository(
        DEFAULT_INVESTMENTS_FILE
    )

    investments = investments_repository.load()

    portfolio = portfolio_engine.build(
        movements,
        investments=investments,
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
        investments=investments,
    )

    print_portfolio(
        portfolio
    )


def run_recommend(
    amount,
    movements_file,
):

    portfolio = load_portfolio(
        movements_file,
        DEFAULT_INVESTMENTS_FILE,
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


def run_invest(
    symbol,
    shares,
    amount,
    portfolio_class,
    movements_file,
    investments_file,
):

    investment_engine = InvestmentEngine()

    investment = investment_engine.create(
        symbol=symbol,
        shares=shares,
        amount=amount,
        portfolio_class=portfolio_class,
        datetime=datetime.now(
            timezone.utc
        ),
    )

    repository = InvestmentRepository(
        investments_file
    )

    repository.save(
        investment
    )

    portfolio = load_portfolio(
        movements_file,
        investments_file,
    )

    position = portfolio.positions.get(
        symbol
    )

    print()
    print(
        "========== INVERSIÓN REGISTRADA =========="
    )
    print()

    print(
        f"Activo       : {investment.symbol}"
    )

    print(
        f"Clase        : "
        f"{investment.portfolio_class}"
    )

    print(
        f"Participaciones : "
        f"{investment.shares}"
    )

    print(
        f"Importe      : "
        f"{investment.amount:.2f} €"
    )

    print(
        f"Precio       : "
        f"{investment.price:.2f} €"
    )

    if position is not None:

        print()

        print(
            f"Posición total : "
            f"{position.shares}"
            f" participaciones"
        )

        print(
            f"Coste total   : "
            f"{position.invested:.2f} €"
        )

        print(
            f"Efectivo      : "
            f"{portfolio.cash:.2f} €"
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

    elif args.command == "invest":

        run_invest(
            symbol=args.symbol,
            shares=args.shares,
            amount=args.amount,
            portfolio_class=args.portfolio_class,
            movements_file=args.movements_file,
            investments_file=args.investments_file,
        )


if __name__ == "__main__":
    main()
