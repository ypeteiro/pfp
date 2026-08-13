from datetime import datetime
from decimal import Decimal, localcontext

from pfp.domain.capital_flow import CapitalFlow, FlowType


class XirrEngine:
    """Calculate annualized money-weighted return from capital flows."""

    def calculate(self, capital_flows, final_value, final_datetime):
        flows = sorted(capital_flows or [], key=lambda flow: flow.datetime)
        if not flows:
            return None

        final_value = Decimal(str(final_value))
        final_datetime = _ensure_aware(final_datetime)
        cash_flows = [
            (_ensure_aware(flow.datetime), -flow.amount if flow.flow_type == FlowType.CONTRIBUTION else flow.amount)
            for flow in flows
        ]
        cash_flows.append((final_datetime, final_value))
        cash_flows = sorted(cash_flows, key=lambda item: item[0])
        if not _has_sign_change(cash_flows):
            return None

        with localcontext() as context:
            context.prec = 50
            return _solve_xirr(cash_flows)


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("XIRR datetimes must be timezone-aware")
    return value


def _has_sign_change(cash_flows):
    has_positive = any(amount > 0 for _, amount in cash_flows)
    has_negative = any(amount < 0 for _, amount in cash_flows)
    return has_positive and has_negative


def _npv_log_rate(log_rate, cash_flows):
    first_datetime = cash_flows[0][0]
    total = Decimal("0")
    for timestamp, amount in cash_flows:
        years = Decimal((timestamp - first_datetime).total_seconds()) / Decimal("31536000")
        total += amount * (-years * log_rate).exp()
    return total


def _solve_xirr(cash_flows):
    """Solve in log(1 + rate) space so very short periods remain numerically stable."""
    low = Decimal("-20")
    high = Decimal("20")
    low_npv = _npv_log_rate(low, cash_flows)
    high_npv = _npv_log_rate(high, cash_flows)

    for _ in range(200):
        if low_npv == 0:
            return low.exp() - Decimal("1")
        if high_npv == 0:
            return high.exp() - Decimal("1")
        if low_npv * high_npv < 0:
            break
        if low_npv > 0 and high_npv > 0:
            high *= Decimal("2")
            high_npv = _npv_log_rate(high, cash_flows)
        else:
            low *= Decimal("2")
            low_npv = _npv_log_rate(low, cash_flows)
    else:
        return None

    for _ in range(300):
        mid = (low + high) / Decimal("2")
        mid_npv = _npv_log_rate(mid, cash_flows)
        if abs(mid_npv) < Decimal("1E-35"):
            return mid.exp() - Decimal("1")
        if low_npv * mid_npv <= 0:
            high = mid
            high_npv = mid_npv
        else:
            low = mid
            low_npv = mid_npv

    return ((low + high) / Decimal("2")).exp() - Decimal("1")
