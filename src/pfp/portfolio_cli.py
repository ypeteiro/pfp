from pfp.cli import load_portfolio
from pfp.market.price_provider import CompositePriceProvider
from pfp.reporting.portfolio_report import PortfolioReport

DEFAULT_INVESTMENTS_FILE = "data/imports/investments.csv"
DEFAULT_SALES_FILE = "data/imports/sales.csv"


def run_portfolio(movements_file, investments_file=DEFAULT_INVESTMENTS_FILE, sales_file=DEFAULT_SALES_FILE, price_provider=None):
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    price_provider = price_provider or CompositePriceProvider()
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    for position in portfolio.positions.values():
        if position.symbol in prices:
            position.market_price = prices[position.symbol]
    report = PortfolioReport.from_portfolio(portfolio)

    print()
    print("========== PATRIMONIO ==========")
    print()
    print(f"{'Cuenta':<24}{'Efectivo':>14}{'Invertido':>14}{'Mercado':>14}{'Patrimonio':>16}")
    print("-" * 82)
    for account in report.accounts:
        market_value = f"{account.market_value:.2f} €" if account.market_value is not None else "N/D"
        total_value = f"{account.total_value:.2f} €" if account.total_value is not None else "N/D"
        print(f"{(account.account_id or account.name):<24}{account.balance:>13.2f} €{account.invested:>13.2f} €{market_value:>14}{total_value:>16}")
    print("-" * 82)
    print(f"{'TOTAL':<24}{report.cash:>13.2f} €{report.invested:>13.2f} €{report.market_value:>13.2f} €{report.total_value:>15.2f} €")
    print()
