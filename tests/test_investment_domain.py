from datetime import datetime, timezone
from decimal import Decimal

import pytest

from pfp.domain.investment import Investment


def _investment(**overrides):
    values = {
        "datetime": datetime(2026, 8, 12, tzinfo=timezone.utc),
        "symbol": "EUNL",
        "shares": Decimal("1.5"),
        "amount": Decimal("150"),
        "price": Decimal("100"),
        "portfolio_class": "RV",
    }
    values.update(overrides)
    return Investment(**values)


def test_investment_accepts_valid_values():
    investment = _investment()

    assert investment.symbol == "EUNL"
    assert investment.shares == Decimal("1.5")
    assert investment.amount == Decimal("150")
    assert investment.price == Decimal("100")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("symbol", "", "Investment symbol cannot be empty"),
        ("shares", Decimal("0"), "Investment shares must be positive"),
        ("amount", Decimal("0"), "Investment amount must be positive"),
        ("price", Decimal("0"), "Investment price must be positive"),
        ("portfolio_class", "", "Investment portfolio_class cannot be empty"),
        ("broker", "", "Investment broker cannot be empty"),
        ("operation_id", "", "Investment operation_id cannot be empty"),
    ],
)
def test_investment_rejects_invalid_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        _investment(**{field: value})
