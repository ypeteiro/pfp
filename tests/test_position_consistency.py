from decimal import Decimal

import pytest

from pfp.domain.position import Position


def test_position_derives_average_price_from_cost_basis():
    position = Position(symbol="EUNL", name="iShares Core MSCI World", shares=Decimal("3"), invested=Decimal("100.50"))
    assert position.average_price == Decimal("100.50") / Decimal("3")


def test_zero_share_position_has_zero_cost_basis():
    position = Position(symbol="EUNL", name="iShares Core MSCI World")
    assert position.shares == Decimal("0")
    assert position.invested == Decimal("0")
    assert position.average_price == Decimal("0")


@pytest.mark.parametrize(
    ("shares", "invested", "average_price"),
    [(Decimal("0"), Decimal("10"), Decimal("0")), (Decimal("2"), Decimal("100"), Decimal("60"))],
)
def test_position_rejects_inconsistent_cost_basis(shares, invested, average_price):
    with pytest.raises(ValueError):
        Position(symbol="EUNL", name="iShares Core MSCI World", shares=shares, invested=invested, average_price=average_price)
