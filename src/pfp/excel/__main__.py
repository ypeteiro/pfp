import argparse
from pathlib import Path

from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE, load_portfolio
from pfp.excel.workbook import WorkbookWriter
from pfp.reporting.portfolio_report import PortfolioReport


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m pfp.excel", description="Export portfolio to Excel")
    parser.add_argument("movements_file")
    parser.add_argument("--output", default="data/reports/pfp.xlsx")
    parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    args = parser.parse_args()

    portfolio = load_portfolio(args.movements_file, args.investments_file, args.sales_file)
    report = PortfolioReport.from_portfolio(portfolio)
    output = WorkbookWriter().write(report, Path(args.output))
    print(f"Excel generado: {output}")


if __name__ == "__main__":
    main()
