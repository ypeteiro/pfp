from datetime import datetime, timezone
from decimal import Decimal

import pytest

from pfp.domain.capital_flow import CapitalFlow, FlowType


def _flow(**overrides):
    values = {
        "datetime": datetime(2026, 8, 12, tzinfo=timezone.utc),
        "amount": Decimal("100"),
        "flow_type": FlowType.CONTRIBUTION,
    }
    values.update(overrides)
    return CapitalFlow(**values)


def test_contribution_has_positive_signed_amount():
    assert _flow(flow_type=FlowType.CONTRIBUTION).signed_amount == Decimal("100")


def test_withdrawal_has_negative_signed_amount():
    assert _flow(flow_type=FlowType.WITHDRAWAL).signed_amount == Decimal("-100")


def test_capital_flow_requires_positive_amount():
    with pytest.raises(ValueError):
        _flow(amount=Decimal("0"))

    with pytest.raises(ValueError):
        _flow(amount=Decimal("-1"))


def test_capital_flow_requires_flow_type():
    with pytest.raises(ValueError):
        _flow(flow_type="CONTRIBUTION")


def test_capital_flow_rejects_blank_transaction_id():
    with pytest.raises(ValueError):
        _flow(transaction_id="   ")


def test_capital_flow_allows_missing_transaction_id():
    assert _flow().transaction_id is None
