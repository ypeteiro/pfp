from datetime import datetime, timedelta, timezone
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.engine.xirr_engine import XirrEngine


def _dt(days=0):
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=days)


def test_xirr_one_year_ten_percent_return():
    flows = [
        CapitalFlow(
            datetime=_dt(),
            amount=Decimal("1000"),
            flow_type=FlowType.CONTRIBUTION,
        )
    ]

    result = XirrEngine().calculate(flows, Decimal("1100"), _dt(365))

    assert abs(result - Decimal("0.10")) < Decimal("1E-20")


def test_xirr_handles_multiple_contributions():
    flows = [
        CapitalFlow(_dt(), Decimal("1000"), FlowType.CONTRIBUTION),
        CapitalFlow(_dt(182), Decimal("1000"), FlowType.CONTRIBUTION),
    ]

    result = XirrEngine().calculate(flows, Decimal("2200"), _dt(365))

    assert result is not None
    assert result > Decimal("0")


def test_xirr_returns_none_without_flows():
    assert XirrEngine().calculate([], Decimal("1100"), _dt(365)) is None


def test_xirr_returns_none_without_sign_change():
    flows = [
        CapitalFlow(_dt(), Decimal("1000"), FlowType.WITHDRAWAL),
    ]

    assert XirrEngine().calculate(flows, Decimal("1100"), _dt(365)) is None
