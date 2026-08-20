import argparse
import hashlib
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from pfp.cli_output import print_portfolio
from pfp.domain.sale import Sale
from pfp.domain.snapshot import PortfolioSnapshot
from pfp.engine.investment_engine import InvestmentEngine
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.engine.rebalance_engine import RebalanceEngine
from pfp.engine.recommendation_engine import RecommendationEngine
from pfp.importers.account_opening_balance_repository import AccountOpeningBalanceRepository
from pfp.importers.account_transfer_repository import AccountTransferRepository
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.snapshot_repository import SnapshotRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider

DEFAULT_INVESTMENTS_FILE = "data/imports/investments.csv"
DEFAULT_SALES_FILE = "data/imports/sales.csv"
DEFAULT_SNAPSHOTS_FILE = "data/imports/snapshots.csv"
DEFAULT_OPENING_BALANCES_FILE = "data/accounts/abanca_ahorro_opening_balance.csv"
DEFAULT_ACCOUNT_TRANSFERS_FILE = "data/accounts/account_transfers.csv"
DEFAULT_ACCOUNT_ID = "Trade Republic"


def build_parser():
    parser = argparse.ArgumentParser(prog="pfp", description="Personal Finance Portfolio")
    subparsers = parser.add_subparsers(dest="command", required=True)
    import_tr_parser = subparsers.add_parser("import-tr", help="Import a Trade Republic CSV")
    import_tr_parser.add_argument("csv_file")
    portfolio_parser = subparsers.add_parser("portfolio", help="Build and value a portfolio")
    portfolio_parser.add_argument("movements_file")
    snapshot_parser = subparsers.add_parser("snapshot", help="Persist the current portfolio state")
    snapshot_parser.add_argument("movements_file")
    snapshot_parser.add_argument("--snapshots-file", default=DEFAULT_SNAPSHOTS_FILE)
    snapshot_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    snapshot_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    recommend_parser = subparsers.add_parser("recommend", help="Recommend where to invest a new contribution")
    recommend_parser.add_argument("amount", type=Decimal)
    recommend_parser.add_argument("movements_file")
    recommend_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    recommend_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    rebalance_parser = subparsers.add_parser("rebalance", help="Calculate or execute portfolio rebalancing")
    rebalance_parser.add_argument("movements_file")
    rebalance_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    rebalance_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    rebalance_parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    rebalance_parser.add_argument("--execute", action="store_true", help="Persist the calculated rebalance orders")
    invest_parser = subparsers.add_parser("invest", help="Register an executed investment")
    invest_parser.add_argument("symbol")
    invest_parser.add_argument("shares", type=Decimal)
    invest_parser.add_argument("amount", type=Decimal)
    invest_parser.add_argument("portfolio_class")
    invest_parser.add_argument("movements_file")
    invest_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    invest_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    invest_parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    invest_order_parser = subparsers.add_parser("invest-order", help="Execute an investment order at the current market price")
    invest_order_parser.add_argument("symbol")
    invest_order_parser.add_argument("amount", type=Decimal)
    invest_order_parser.add_argument("movements_file")
    invest_order_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    invest_order_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    invest_order_parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    sell_parser = subparsers.add_parser("sell", help="Register an executed sale")
    sell_parser.add_argument("symbol")
    sell_parser.add_argument("shares", type=Decimal)
    sell_parser.add_argument("amount", type=Decimal)
    sell_parser.add_argument("movements_file")
    sell_parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    sell_parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    sell_parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    return parser


def load_portfolio(movements_file, investments_file=None, sales_file=None, opening_balances_file=DEFAULT_OPENING_BALANCES_FILE, account_transfers_file=DEFAULT_ACCOUNT_TRANSFERS_FILE):
    movements = TradeRepublicImporter().load(movements_file)
    investments = InvestmentRepository(investments_file).load() if investments_file is not None else None
    sales = SaleRepository(sales_file).load() if sales_file is not None else None
    opening_balances = AccountOpeningBalanceRepository(opening_balances_file).load()
    account_transfers = AccountTransferRepository(account_transfers_file).load()
    return PortfolioEngine().build(movements, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)


def run_import_tr(csv_file):
    print_portfolio(load_portfolio(csv_file))


def run_portfolio(movements_file):
    importer = TradeRepublicImporter()
    price_provider = CompositePriceProvider()
    portfolio_engine = PortfolioEngine()
    movements = importer.load(movements_file)
    investments = InvestmentRepository(DEFAULT_INVESTMENTS_FILE).load()
    sales = SaleRepository(DEFAULT_SALES_FILE).load()
    opening_balances = AccountOpeningBalanceRepository(DEFAULT_OPENING_BALANCES_FILE).load()
    account_transfers = AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE).load()
    portfolio = portfolio_engine.build(movements, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    portfolio = portfolio_engine.build(movements, prices, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)
    print_portfolio(portfolio)


def run_snapshot(movements_file, snapshots_file=DEFAULT_SNAPSHOTS_FILE, investments_file=DEFAULT_INVESTMENTS_FILE, sales_file=DEFAULT_SALES_FILE, price_provider=None):
    price_provider = price_provider or CompositePriceProvider()
    movements = TradeRepublicImporter().load(movements_file)
    investments = InvestmentRepository(investments_file).load()
    sales = SaleRepository(sales_file).load()
    opening_balances = AccountOpeningBalanceRepository(DEFAULT_OPENING_BALANCES_FILE).load()
    account_transfers = AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE).load()
    engine = PortfolioEngine()
    portfolio = engine.build(movements, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    portfolio = engine.build(movements, prices, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)
    market_value = sum((position.market_value or Decimal("0")) for position in portfolio.positions.values())
    unrealized = sum((position.gain_loss or Decimal("0")) for position in portfolio.positions.values())
    class_values = {"EQUITY": Decimal("0"), "FIXED_INCOME": Decimal("0"), "GOLD": Decimal("0"), "CRYPTO": Decimal("0")}
    for position in portfolio.positions.values():
        portfolio_class = position.portfolio_class or "CRYPTO"
        if portfolio_class in class_values:
            class_values[portfolio_class] += position.market_value or Decimal("0")
    snapshot = PortfolioSnapshot(
        datetime=datetime.now(timezone.utc),
        total_value=portfolio.cash + market_value,
        cash=portfolio.cash,
        invested_cost=portfolio.invested,
        market_value=market_value,
        realized_gain_loss=portfolio.realized_gain_loss,
        unrealized_gain_loss=unrealized,
        equity_value=class_values["EQUITY"],
        fixed_income_value=class_values["FIXED_INCOME"],
        gold_value=class_values["GOLD"],
        crypto_value=class_values["CRYPTO"],
    )
    SnapshotRepository(snapshots_file).save(snapshot)
    print()
    print("========== SNAPSHOT ==========")
    print()
    print(f"Patrimonio total : {snapshot.total_value:.2f} €")
    print(f"Efectivo         : {snapshot.cash:.2f} €")
    print(f"Valor mercado    : {snapshot.market_value:.2f} €")
    print(f"Coste invertido  : {snapshot.invested_cost:.2f} €")
    print(f"P/L no realizado : {snapshot.unrealized_gain_loss:.2f} €")
    print(f"P/L realizado    : {snapshot.realized_gain_loss:.2f} €")
    print(f"Guardado en      : {snapshots_file}")
    print()


def run_recommend(amount, movements_file, investments_file=DEFAULT_INVESTMENTS_FILE, sales_file=DEFAULT_SALES_FILE):
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    recommendation = RecommendationEngine().recommend(portfolio, amount)
    print()
    print("========== ORDEN DE INVERSIÓN ==========")
    print()
    print(f"Aportación total : {recommendation.total_amount:.2f} €")
    print()
    for order in recommendation.orders:
        print(f"  {order.amount:.2f} € → {order.symbol} ({order.asset_name})")
    print()
    print("Comandos ejecutables:")
    print()
    for order in recommendation.orders:
        print("  python -m pfp invest-order " f"{order.symbol} {order.amount:.2f} {movements_file}" f" --investments-file {investments_file}" f" --sales-file {sales_file}")
    print()
    print(f"TOTAL             : {recommendation.total_amount:.2f} €")
    print()


def _build_rebalance(movements_file, investments_file, sales_file, price_provider, account_id=DEFAULT_ACCOUNT_ID):
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    movements = TradeRepublicImporter().load(movements_file)
    investments = InvestmentRepository(investments_file).load()
    sales = SaleRepository(sales_file).load()
    opening_balances = AccountOpeningBalanceRepository(DEFAULT_OPENING_BALANCES_FILE).load()
    account_transfers = AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE).load()
    portfolio = PortfolioEngine().build(movements, prices, investments=investments, sales=sales, opening_balances=opening_balances, account_transfers=account_transfers)
    return RebalanceEngine().rebalance(portfolio, account_id=account_id)


def _rebalance_operation_id(rebalance, order, account_id=DEFAULT_ACCOUNT_ID):
    payload = "|".join(("rebalance", account_id, str(rebalance.total_value), order.action, order.symbol, order.portfolio_class, str(order.amount), str(order.shares)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _execute_rebalance(rebalance, movements_file, investments_file, sales_file, price_provider, account_id=DEFAULT_ACCOUNT_ID):
    current = _build_rebalance(movements_file, investments_file, sales_file, price_provider, account_id=account_id)
    if current != rebalance:
        raise ValueError("Portfolio changed since rebalance calculation")
    for order in rebalance.orders:
        operation_id = _rebalance_operation_id(rebalance, order, account_id=account_id)
        if order.action == "SELL":
            run_sell(order.symbol, order.shares, order.amount, movements_file, sales_file, investments_file, operation_id, account_id)
    for order in rebalance.orders:
        operation_id = _rebalance_operation_id(rebalance, order, account_id=account_id)
        if order.action == "BUY":
            run_invest_order(order.symbol, order.amount, movements_file, investments_file, price_provider, sales_file, operation_id, account_id)


def run_rebalance(movements_file, investments_file=DEFAULT_INVESTMENTS_FILE, sales_file=DEFAULT_SALES_FILE, price_provider=None, execute=False, account_id=DEFAULT_ACCOUNT_ID):
    price_provider = price_provider or CompositePriceProvider()
    rebalance = _build_rebalance(movements_file, investments_file, sales_file, price_provider, account_id=account_id)
    print()
    print("========== REBALANCEO ==========")
    print()
    print(f"Cuenta rebalanceada     : {account_id}")
    print(f"Patrimonio total        : {rebalance.total_value:.2f} €")
    print(f"Patrimonio rebalanceable: {rebalance.rebalanceable_value:.2f} €")
    excluded_value = rebalance.total_value - rebalance.rebalanceable_value
    if excluded_value > 0:
        print(f"No rebalanceable        : {excluded_value:.2f} €")
    print()
    print("## ASIGNACIÓN")
    print()
    for allocation in rebalance.allocations:
        print(f"{allocation.portfolio_class:<16}" f" actual {allocation.current_percent:7.2f} %" f" objetivo {allocation.target_percent:7.2f} %" f" diferencia {allocation.difference_percent:7.2f} %")
    print()
    print("## ÓRDENES")
    print()
    if not rebalance.orders:
        print("Portfolio ya rebalanceado.")
    else:
        for order in rebalance.orders:
            print(f"{order.action:<5}" f" {order.symbol:<18}" f" {order.amount:10.2f} €" f" ({order.portfolio_class})")
        print()
        if execute:
            _execute_rebalance(rebalance, movements_file, investments_file, sales_file, price_provider, account_id=account_id)
            print("Rebalanceo ejecutado y persistido.")
        else:
            print("Comandos ejecutables:")
            print()
            for order in rebalance.orders:
                if order.action == "BUY":
                    print("  python -m pfp invest-order " f"{order.symbol} {order.amount:.2f} {movements_file}" f" --investments-file {investments_file}" f" --sales-file {sales_file}" f" --account-id {account_id}")
                else:
                    print("  python -m pfp sell " f"{order.symbol} {order.shares} {order.amount:.2f} {movements_file}" f" --investments-file {investments_file}" f" --sales-file {sales_file}" f" --account-id {account_id}")
    print()


def run_invest(symbol, shares, amount, portfolio_class, movements_file, investments_file, sales_file=DEFAULT_SALES_FILE, operation_id=None, account_id=DEFAULT_ACCOUNT_ID):
    investment = InvestmentEngine().create(symbol=symbol, shares=shares, amount=amount, portfolio_class=portfolio_class, datetime=datetime.now(timezone.utc), account_id=account_id)
    investment = replace(investment, operation_id=operation_id)
    InvestmentRepository(investments_file).save(investment)
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    position = portfolio.positions.get(symbol)
    print()
    print("========== INVERSIÓN REGISTRADA ==========")
    print()
    print(f"Activo       : {investment.symbol}")
    print(f"Clase        : {investment.portfolio_class}")
    print(f"Cuenta       : {investment.account_id}")
    print(f"Participaciones : {investment.shares}")
    print(f"Importe      : {investment.amount:.2f} €")
    print(f"Precio       : {investment.price:.2f} €")
    if position is not None:
        print()
        print(f"Posición total : {position.shares} participaciones")
        print(f"Coste total   : {position.invested:.2f} €")
        print(f"Efectivo      : {portfolio.cash:.2f} €")
    print()


def run_invest_order(symbol, amount, movements_file, investments_file, price_provider=None, sales_file=DEFAULT_SALES_FILE, operation_id=None, account_id=DEFAULT_ACCOUNT_ID):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    position = portfolio.positions.get(symbol)
    if position is None:
        raise ValueError("Symbol is not present in portfolio")
    price_provider = price_provider or CompositePriceProvider()
    prices = price_provider.get_prices([symbol])
    price = prices.get(symbol)
    if price is None:
        raise ValueError(f"Market price is not available for {symbol}")
    shares = amount / price
    run_invest(symbol, shares, amount, position.portfolio_class, movements_file, investments_file, sales_file, operation_id, account_id)


def run_sell(symbol, shares, amount, movements_file, sales_file=DEFAULT_SALES_FILE, investments_file=DEFAULT_INVESTMENTS_FILE, operation_id=None, account_id=DEFAULT_ACCOUNT_ID):
    shares = Decimal(str(shares))
    amount = Decimal(str(amount))
    if shares <= 0:
        raise ValueError("Shares must be greater than zero")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    position = portfolio.positions.get(symbol)
    if position is None:
        raise ValueError("Symbol is not present in portfolio")
    if shares > position.shares:
        raise ValueError("Insufficient shares")
    sale = Sale(datetime=datetime.now(timezone.utc), symbol=symbol, shares=shares, amount=amount, price=amount / shares, operation_id=operation_id, account_id=account_id)
    SaleRepository(sales_file).save(sale)
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    position = portfolio.positions.get(symbol)
    print()
    print("========== VENTA REGISTRADA ==========")
    print()
    print(f"Activo          : {sale.symbol}")
    print(f"Cuenta          : {sale.account_id}")
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
    args = build_parser().parse_args()
    if args.command == "import-tr":
        run_import_tr(args.csv_file)
    elif args.command == "portfolio":
        run_portfolio(args.movements_file)
    elif args.command == "snapshot":
        run_snapshot(args.movements_file, args.snapshots_file, args.investments_file, args.sales_file)
    elif args.command == "recommend":
        run_recommend(args.amount, args.movements_file, args.investments_file, args.sales_file)
    elif args.command == "rebalance":
        run_rebalance(args.movements_file, args.investments_file, args.sales_file, execute=args.execute, account_id=args.account_id)
    elif args.command == "invest":
        run_invest(args.symbol, args.shares, args.amount, args.portfolio_class, args.movements_file, args.investments_file, args.sales_file, account_id=args.account_id)
    elif args.command == "invest-order":
        run_invest_order(args.symbol, args.amount, args.movements_file, args.investments_file, sales_file=args.sales_file, account_id=args.account_id)
    elif args.command == "sell":
        run_sell(args.symbol, args.shares, args.amount, args.movements_file, args.sales_file, args.investments_file, account_id=args.account_id)
