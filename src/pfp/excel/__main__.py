import argparse
from pathlib import Path

from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE, load_portfolio
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.excel.workbook import WorkbookWriter
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider
from pfp.reporting.portfolio_report import PortfolioReport


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m pfp.excel", description="Export portfolio to Excel")
    parser.add_argument("movements_file")
    parser.add_argument("--output", default="data/reports/pfp.xlsx")
    parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    args = parser.parse_args()

    portfolio = load_portfolio(args.movements_file, args.investments_file, args.sales_file)
    prices = CompositePriceProvider().get_prices(list(portfolio.positions.keys()))
    movements = TradeRepublicImporter().load(args.movements_file)
    investments = InvestmentRepository(args.investments_file).load()
    sales = SaleRepository(args.sales_file).load()
    portfolio = PortfolioEngine().build(movements, prices, investments=investments, sales=sales)

    report = PortfolioReport.from_portfolio(portfolio)
    output = WorkbookWriter().write(report, Path(args.output))
    print(f"Excel generado: {output}")


if __name__ == "__main__":
    main()
