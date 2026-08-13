from decimal import Decimal

import pytest

from pfp.domain.position import Position


def test_position_allows_zero_values_for_closed_position():
    position = Position(
        symbol="TEST",
        name="Test",
        shares=Decimal("0"),
        invested=Decimal("0"),
        average_price=Decimal("0"),
    )

    assert position.shares == Decimal("0")
    assert position.invested == Decimal("0")
    assert position.average_price == Decimal("0")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("shares", Decimal("-1"), "Shares cannot be negative"),
        ("invested", Decimal("-1"), "Invested amount cannot be negative"),
        ("average_price", Decimal("-1"), "Average price cannot be negative"),
    ],
)
def test_position_rejects_negative_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        Position(symbol="TEST", name="Test", **{field: value})


def test_position_market_value_and_gain_loss_are_unchanged():
    position = Position(
        symbol="TEST",
        name="Test",
        shares=Decimal("2"),
        invested=Decimal("150"),
        average_price=Decimal("75"),
        market_price=Decimal("100"),
    )

    assert position.market_value == Decimal("200")
    assert position.gain_loss == Decimal("50")
