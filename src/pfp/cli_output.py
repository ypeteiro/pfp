from pfp.domain.portfolio import Portfolio


def print_portfolio(portfolio: Portfolio) -> None:
    print()
    print("========== CARTERA ==========")
    print()

    print(f"Efectivo : {portfolio.cash:.2f}")
    print(f"Invertido: {portfolio.invested:.2f}")
    print()

    for position in portfolio.positions.values():
        print(
            f"{position.symbol:15}"
            f"{position.shares:>15}"
            f"{position.average_price:>15.2f}"
        )