import argparse
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from pfp.cli_output import print_portfolio
from pfp.domain.sale import Sale
from pfp.engine.investment_engine import InvestmentEngine
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.engine.recommendation_engine import RecommendationEngine
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider


DEFAULT_INVESTMENTS_FILE = "data/imports/investments.csv"
DEFAULT_SALES_FILE = "data/imports/sales.csv"


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
    import_tr_parser.add_argument("csv_file")

    portfolio_parser = subparsers.add_parser(
        "portfolio",
        help="Build and value a portfolio",
    )
    portfolio_parser.add_argument("movements_file")

    recommend_parser = subparsers.add_parser(
        "recommend",
        help="Recommend where to invest a new contribution",
    )
    recommend_parser.add_argument("amount", type=Decimal)
    recommend_parser.add_argument("movements_file")
    recommend_parser.add_argument(
        "--investments-file",
        default=DEFAULT_INVESTMENTS_FILE,
    )
    recommend_parser.add_argument(
        "--sales-file",
        default=DEFAULT_SALES_FILE,
    )

    invest_parser = subparsers.add_parser(
        "invest",
        help="Register an executed investment",
    )
    invest_parser.add_argument("symbol")
    invest_parser.add_argument("shares", type=Decimal)
    invest_parser.add_argument("amount", type=Decimal)
    invest_parser.add_argument("portfolio_class")
    invest_parser.add_argument("movements_file")
    invest_parser.add_argument(
        "--investments-file",
        default=DEFAULT_INVESTMENTS_FILE,
    )
    invest_parser.add_argument(
        "--sales-file",
        default=DEFAULT_SALES_FILE,
    )

    invest_order_parser = subparsers.add_parser(
        "invest-order",
        help="Execute an investment order at the current market price",
    )
    invest_order_parser.add_argument("symbol")
    invest_order_parser.add_argument("amount", type=Decimal)
    invest_order_parser.add_argument("movements_file")
    invest_order_parser.add_argument(
        "--investments-file",
        default=DEFAULT_INVESTMENTS_FILE,
    )
    invest_order_parser.add_argument(
        "--sales-file",
        default=DEFAULT_SALES_FILE,
    )

    sell_parser = subparsers.add_parser(
        "sell",
        help="Register an executed sale",
    )
    sell_parser.add_argument("symbol")
    sell_parser.add_argument("shares", type=Decimal)
    sell_parser.add_argument("amount", type=Decimal)
    sell_parser.add_argument("movements_file")
    sell_parser.add_argument(
        "--investments-file",
        default=DEFAULT_INVESTMENTS_FILE,
    )
    sell_parser.add_argument(
        "--sales-file",
        default=DEFAULT_SALES_FILE,
    )

    return parser


def load_portfolio(movements_file, investments_file=None, sales_file=None):
    importer = TradeRepublicImporter()
    movements = importer.load(movements_file)

    investments = None
    if investments_file is not None:
        investments = InvestmentRepository(investments_file).load()

    sales = None
    if sales_file is not None:
        sales = SaleRepository(sales_file).load()

    return PortfolioEngine().build(
        movements,
        investments=investments,
        sales=sales,
    )


def run_import_tr(csv_file):
    portfolio = load_portfolio(csv_file)
    print_portfolio(portfolio)


def run_portfolio(movements_file):
    importer = TradeRepublicImporter()
    price_provider = CompositePriceProvider()
    portfolio_engine = PortfolioEngine()

    movements = importer.load(movements_file)
    investments_repository = InvestmentRepository(DEFAULT_INVESTMENTS_FILE)
    investments = investments_repository.load()
    sales = SaleRepository(DEFAULT_SALES_FILE).load()

    portfolio = portfolio_engine.build(
        movements,
        investments=investments,
        sales=sales,
    )

    symbols = list(portfolio.positions.keys())
    prices = price_provider.get_prices(symbols)

    portfolio = portfolio_engine.build(
        movements,
        prices,
        investments=investments,
        sales=sales,
    )

    print_portfolio(portfolio)


def run_recommend(amount, movements_file, investments_file=DEFAULT_INVESTMENTS_FILE, sales_file=DEFAULT_SALES_FILE):
    portfolio = load_portfolio(
        movements_file,
        investments_file,
        sales_file,
    )

    recommendation = RecommendationEngine().recommend(
        portfolio,
        amount,
    )

    print()
    print("========== ORDEN DE INVERSIÓN ==========")
    print()

    print(f"Aportación total : {recommendation.total_amount:.2f} €")
    print()

    for order in recommendation.orders:
        print(
            f"  {order.amount:.2f} € "
            f"→ {order.symbol} "
            f"({order.asset_name})"
        )

    print()
    print("Comandos ejecutables:")
    print()

    for order in recommendation.orders:
        print(
            "  python -m pfp invest-order "
            f"{order.symbol} "
            f"{order.amount:.2f} "
            f"{movements_file}"
            f" --investments-file {investments_file}"
            f" --sales-file {sales_file}"
        )

    print()
    print(f"TOTAL             : {recommendation.total_amount:.2f} €")
    print()


def run_invest(
    symbol,
    shares,
    amount,
    portfolio_class,
    movements_file,
    investments_file,
):
    investment = InvestmentEngine().create(
        symbol=symbol,
        shares=shares,
        amount=amount,
        portfolio_class=portfolio_class,
        datetime=datetime.now(timezone.utc),
    )

    InvestmentRepository(investments_file).save(investment)

    portfolio = load_portfolio(
        movements_file,
        investments_file,
    )
    position = portfolio.positions.get(symbol)

    print()
    print("========== INVERSIÓN REGISTRADA ==========")
    print()
    print(f"Activo       : {investment.symbol}")
    print(f"Clase        : {investment.portfolio_class}")
    print(f"Participaciones : {investment.shares}")
    print(f"Importe      : {investment.amount:.2f} €")
    print(f"Precio       : {investment.price:.2f} €")

    if position is not None:
        print()
        print(f"Posición total : {position.shares} participaciones")
        print(f"Coste total   : {position.invested:.2f} €")
        print(f"Efectivo      : {portfolio.cash:.2f} €")

    print()


def run_invest_order(
    symbol,
    amount,
    movements_file,
    investments_file,
    price_provider=None,
    sales_file=DEFAULT_SALES_FILE,
):
    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    portfolio = load_portfolio(
        movements_file,
        investments_file,
        sales_file,
    )
    position = portfolio.positions.get(symbol)

    if position is None:
        raise ValueError("Symbol is not present in portfolio")

    price_provider = price_provider or CompositePriceProvider()
    price = price_provider.get_prices([symbol]).get(symbol)

    if price is None:
        raise ValueError("Price is not available for symbol")

    shares = amount / price

    run_invest(
        symbol=symbol,
        shares=shares,
        amount=amount,
        portfolio_class=position.portfolio_class,
        movements_file=movements_file,
        investments_file=investments_file,
    )


def run_sell(
    symbol,
    shares,
    amount,
    movements_file,
    sales_file=DEFAULT_SALES_FILE,
    investments_file=DEFAULT_INVESTMENTS_FILE,
):
    shares = Decimal(str(shares))
    amount = Decimal(str(amount))

    if shares <= 0:
        raise ValueError("Shares must be greater than zero")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    portfolio = load_portfolio(
        movements_file,
        investments_file,
        sales_file,
    )
    position = portfolio.positions.get(symbol)

    if position is None:
        raise ValueError("Symbol is not present in portfolio")
    if shares > position.shares:
        raise ValueError("Insufficient shares")

    sale = Sale(
        datetime=datetime.now(timezone.utc),
        symbol=symbol,
        shares=shares,
        amount=amount,
        price=amount / shares,
    )

    SaleRepository(sales_file).save(sale)

    portfolio = load_portfolio(
        movements_file,
        investments_file,
        sales_file,
    )
    position = portfolio.positions.get(symbol)

    print()
    print("========== VENTA REGISTRADA ==========")
    print()
    print(f"Activo          : {sale.symbol}")
    print(f"Participaciones : {sale.shares}")
    print(f"Importe         : {sale.amount:.2f} €")
    print(f"Precio          : {sale.price:.2f} €")
    print(f"P/L realizado   : {portfolio.realized_gain_loss:.2f} €")

    if position is not None:
        print()
        print(f"Posición total  : {position.shares} participaciones")
        print(f"Coste restante  : {position.invested:.2f} €")
        print(f"Efectivo        : {portfolio.cash:.2f} €")

    print()


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "import-tr":
        run_import_tr(args.csv_file)
    elif args.command == "portfolio":
        run_portfolio(args.movements_file)
    elif args.command == "recommend":
        run_recommend(args.amount, args.movements_file, args.investments_file, args.sales_file)
    elif args.command == "invest":
        run_invest(
            symbol=args.symbol,
            shares=args.shares,
            amount=args.amount,
            portfolio_class=args.portfolio_class,
            movements_file=args.movements_file,
            investments_file=args.investments_file,
        )
    elif args.command == "invest-order":
        run_invest_order(
            symbol=args.symbol,
            amount=args.amount,
            movements_file=args.movements_file,
            investments_file=args.investments_file,
            sales_file=args.sales_file,
        )
    elif args.command == "sell":
        run_sell(
            symbol=args.symbol,
            shares=args.shares,
            amount=args.amount,
            movements_file=args.movements_file,
            investments_file=args.investments_file,
            sales_file=args.sales_file,
        )


if __name__ == "__main__":
    main()
