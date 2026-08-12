from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType


def test_contribution_has_positive_signed_amount():
    flow = CapitalFlow(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        amount=Decimal("800"),
        flow_type=FlowType.CONTRIBUTION,
    )

    assert flow.signed_amount == Decimal("800")


def test_withdrawal_has_negative_signed_amount():
    flow = CapitalFlow(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        amount=Decimal("250"),
        flow_type=FlowType.WITHDRAWAL,
    )

    assert flow.signed_amount == Decimal("-250")
