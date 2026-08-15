from datetime import datetime
from decimal import Decimal

from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.sale import Sale


WHEN = datetime(2026, 1, 1)


def test_full_sale_closes_position_and_resets_cost_basis():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("4"), Decimal("400"), Decimal("100"), "RV")
    )

    portfolio.add_sale(
        Sale(WHEN, "EUNL", Decimal("4"), Decimal("480"), Decimal("120"))
    )

    position = portfolio.positions["EUNL"]
    assert portfolio.cash == Decimal("1080")
    assert portfolio.invested == Decimal("0")
    assert portfolio.realized_gain_loss == Decimal("80")
    assert position.shares == Decimal("0")
    assert position.invested == Decimal("0")
    assert position.average_price == Decimal("0")


def test_reinvestment_after_full_sale_starts_a_new_cost_basis():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("4"), Decimal("400"), Decimal("100"), "RV")
    )
    portfolio.add_sale(
        Sale(WHEN, "EUNL", Decimal("4"), Decimal("480"), Decimal("120"))
    )
    portfolio.add_investment(
        Investment(WHEN, "EUNL", Decimal("2"), Decimal("300"), Decimal("150"), "RV")
    )

    position = portfolio.positions["EUNL"]
    assert portfolio.cash == Decimal("780")
    assert portfolio.invested == Decimal("300")
    assert portfolio.realized_gain_loss == Decimal("80")
    assert position.shares == Decimal("2")
    assert position.invested == Decimal("300")
    assert position.average_price == Decimal("150")


def test_partial_sale_preserves_cost_basis_with_decimal_shares():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.add_investment(
        Investment(
            WHEN,
            "EUNL",
            Decimal("3.75"),
            Decimal("412.50"),
            Decimal("110"),
            "RV",
        )
    )

    portfolio.add_sale(
        Sale(WHEN, "EUNL", Decimal("1.25"), Decimal("162.50"), Decimal("130"))
    )

    position = portfolio.positions["EUNL"]
    assert position.shares == Decimal("2.50")
    assert position.invested == Decimal("275.00")
    assert position.average_price == Decimal("110")
    assert portfolio.invested == Decimal("275.00")
    assert portfolio.realized_gain_loss == Decimal("25.00")
