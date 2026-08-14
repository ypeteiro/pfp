from datetime import datetime, timezone
from decimal import Decimal

import pytest

from pfp.domain.sale import Sale


def _sale(**overrides):
    values = {
        "datetime": datetime(2026, 8, 13, tzinfo=timezone.utc),
        "symbol": "EUNL",
        "shares": Decimal("2"),
        "amount": Decimal("200"),
        "price": Decimal("100"),
        "broker": "Trade Republic",
        "operation_id": "sale-1",
    }
    values.update(overrides)
    return Sale(**values)


@pytest.mark.parametrize("field", ["symbol", "broker"])
def test_sale_rejects_empty_text(field):
    with pytest.raises(ValueError):
        _sale(**{field: "   "})


@pytest.mark.parametrize("field", ["shares", "amount", "price"])
def test_sale_rejects_non_positive_numeric_values(field):
    with pytest.raises(ValueError):
        _sale(**{field: Decimal("0")})

    with pytest.raises(ValueError):
        _sale(**{field: Decimal("-1")})


def test_sale_rejects_empty_operation_id():
    with pytest.raises(ValueError):
        _sale(operation_id=" ")


def test_sale_allows_missing_operation_id():
    sale = _sale(operation_id=None)
    assert sale.operation_id is None
