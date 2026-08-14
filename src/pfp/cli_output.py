from collections import defaultdict
from decimal import Decimal

from pfp.domain.portfolio import Portfolio


PORTFOLIO_CLASS_LABELS = {
    "EQUITY": "Renta variable",
    "FIXED_INCOME": "Renta fija",
    "GOLD": "Oro",
    "CRYPTO": "Crypto",
    "UNKNOWN": "Sin clasificar",
}


TARGET_ALLOCATION = {
    "EQUITY": Decimal("75"),
    "FIXED_INCOME": Decimal("20"),
    "GOLD": Decimal("5"),
}


def _normalized_class(
    portfolio_class: str | None,
) -> str:
    if portfolio_class is None:
        return "UNKNOWN"

    return portfolio_class


def _class_label(
    portfolio_class: str | None,
) -> str:

    normalized_class = _normalized_class(
        portfolio_class
    )

    return PORTFOLIO_CLASS_LABELS.get(
        normalized_class,
        normalized_class,
    )


def print_portfolio(
    portfolio: Portfolio,
) -> None:

    market_invested = Decimal("0")
    missing_prices = []

    for position in portfolio.positions.values():

        if position.market_value is None:

            missing_prices.append(
                position.symbol
            )

        else:

            market_invested += (
                position.market_value
            )

    market_total = (
        portfolio.cash
        + market_invested
    )

    print()
    print("========== PFP ==========")
    print()

    print(
        f"Efectivo             : "
        f"{portfolio.cash:.2f} €"
    )

    print(
        f"Coste invertido      : "
        f"{portfolio.invested:.2f} €"
    )

    if missing_prices:

        print(
            "Valor mercado        : N/D"
        )

    else:

        print(
            f"Valor mercado        : "
            f"{market_invested:.2f} €"
        )

        print(
            f"Patrimonio mercado   : "
            f"{market_total:.2f} €"
        )

    print()

    print("POSICIONES")
    print("-" * 100)

    for position in portfolio.positions.values():

        if position.market_value is None:

            market_value = "N/D"
            gain_loss = "N/D"

        else:

            market_value = (
                f"{position.market_value:.2f} €"
            )

            gain_loss = (
                f"{position.gain_loss:.2f} €"
            )

        print(
            f"{position.symbol:15}"
            f"{position.shares:>15}"
            f"  coste {position.invested:>10.2f} €"
            f"  mercado {market_value:>12}"
            f"  P/L {gain_loss:>12}"
        )

    print()

    if missing_prices:

        print("PRECIOS PENDIENTES")
        print("-" * 80)

        for symbol in missing_prices:
            print(symbol)

        print()

        print(
            "Añade los precios actuales en "
            "src/pfp/domain/market_prices.py."
        )

        return

    invested_by_class = defaultdict(
        lambda: Decimal("0")
    )

    for position in portfolio.positions.values():

        portfolio_class = _normalized_class(
            position.portfolio_class
        )

        invested_by_class[
            portfolio_class
        ] += position.market_value

    print("ASIGNACIÓN DE MERCADO")
    print("-" * 80)

    for portfolio_class, amount in sorted(
        invested_by_class.items()
    ):

        if market_invested:

            percentage = (
                amount
                / market_invested
                * Decimal("100")
            )

        else:

            percentage = Decimal("0")

        print(
            f"{_class_label(portfolio_class):20}"
            f"{percentage:>8.2f} %"
        )

    print()

    print("OBJETIVO")
    print("-" * 80)

    for portfolio_class, target in (
        TARGET_ALLOCATION.items()
    ):

        current_amount = invested_by_class.get(
            portfolio_class,
            Decimal("0"),
        )

        if market_invested:

            current_percentage = (
                current_amount
                / market_invested
                * Decimal("100")
            )

        else:

            current_percentage = Decimal("0")

        difference = (
            current_percentage
            - target
        )

        print(
            f"{_class_label(portfolio_class):20}"
            f"actual {current_percentage:>7.2f} %"
            f"  objetivo {target:>7.2f} %"
            f"  diferencia {difference:>7.2f} %"
        )

    print()