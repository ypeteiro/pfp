import argparse
from decimal import Decimal

from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE, load_portfolio
from pfp.reporting.portfolio_report import PortfolioReport


def _money(value: Decimal) -> str:
    return f"{value:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")


def _bar(percent: Decimal, width: int = 24) -> str:
    filled = max(0, min(width, round(float(percent) / 100 * width)))
    return "#" * filled + "-" * (width - filled)


def print_dashboard(report: PortfolioReport) -> None:
    print()
    print("+----------------------------------------------+")
    print("|                 PFP DASHBOARD                |")
    print("+----------------------------------------------+")
    print(f"| Patrimonio       {_money(report.total_value):>25} |")
    print(f"| Invertido        {_money(report.invested):>25} |")
    print(f"| Efectivo         {_money(report.cash):>25} |")
    print(f"| Valor mercado    {_money(report.market_value):>25} |")
    print(f"| P/L realizado    {_money(report.realized_gain_loss):>25} |")
    print(f"| P/L no realizado {_money(report.unrealized_gain_loss):>25} |")
    print("+----------------------------------------------+")
    print("| DISTRIBUCION                                  |")

    classes = (
        ("Renta variable", report.equity_value),
        ("Renta fija", report.fixed_income_value),
        ("Oro", report.gold_value),
        ("Crypto", report.crypto_value),
    )
    invested = report.market_value
    for label, value in classes:
        percent = value / invested * Decimal("100") if invested else Decimal("0")
        print(f"| {label:<16} {_bar(percent)} {percent:>6.2f} % |")

    print("+----------------------------------------------+")
    print("| POSICIONES                                    |")
    for position in report.positions:
        value = _money(position.market_value) if position.market_value is not None else "N/D"
        print(f"| {position.symbol:<18} {value:>23} |")
    print("+----------------------------------------------+")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m pfp.dashboard")
    parser.add_argument("movements_file")
    parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    args = parser.parse_args()

    portfolio = load_portfolio(args.movements_file, args.investments_file, args.sales_file)
    report = PortfolioReport.from_portfolio(portfolio)
    print_dashboard(report)


if __name__ == "__main__":
    main()
