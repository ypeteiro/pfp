from decimal import Decimal

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


def test_market_value_sums_priced_positions() -> None:
    portfolio = Portfolio(
        positions={
            "VWCE": Position(
                symbol="VWCE",
                name="Vanguard FTSE All-World",
                shares=Decimal("2"),
                invested=Decimal("200"),
                average_price=Decimal("100"),
                market_price=Decimal("120"),
            ),
            "EUNL": Position(
                symbol="EUNL",
                name="iShares Core MSCI World",
                shares=Decimal("3"),
                invested=Decimal("300"),
                average_price=Decimal("100"),
                market_price=Decimal("110"),
            ),
        },
        cash=Decimal("50"),
        invested=Decimal("500"),
    )

    assert portfolio.market_value == Decimal("570")
    assert portfolio.total_value == Decimal("620")
    assert portfolio.unrealized_gain_loss == Decimal("70")


def test_market_value_is_unknown_when_a_position_has_no_price() -> None:
    portfolio = Portfolio(
        positions={
            "VWCE": Position(
                symbol="VWCE",
                name="Vanguard FTSE All-World",
                shares=Decimal("2"),
                invested=Decimal("200"),
                average_price=Decimal("100"),
            )
        },
        cash=Decimal("50"),
        invested=Decimal("200"),
    )

    assert portfolio.market_value is None
    assert portfolio.total_value is None
    assert portfolio.unrealized_gain_loss is None
