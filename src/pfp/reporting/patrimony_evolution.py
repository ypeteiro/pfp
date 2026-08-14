"""Patrimony evolution derived from historical capital flows."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType


@dataclass(frozen=True, slots=True)
class PatrimonyPoint:
    datetime: datetime
    contribution: Decimal
    withdrawal: Decimal
    net_flow: Decimal
    cumulative_contributed: Decimal


@dataclass(frozen=True, slots=True)
class PatrimonyEvolution:
    points: tuple[PatrimonyPoint, ...]
    total_contributions: Decimal
    total_withdrawals: Decimal
    net_contributions: Decimal

    @classmethod
    def from_capital_flows(cls, flows: list[CapitalFlow] | tuple[CapitalFlow, ...]) -> "PatrimonyEvolution":
        ordered = sorted(flows, key=lambda flow: flow.datetime)
        cumulative = Decimal("0")
        points: list[PatrimonyPoint] = []
        contributions = Decimal("0")
        withdrawals = Decimal("0")
        for flow in ordered:
            contribution = flow.amount if flow.flow_type == FlowType.CONTRIBUTION else Decimal("0")
            withdrawal = flow.amount if flow.flow_type == FlowType.WITHDRAWAL else Decimal("0")
            contributions += contribution
            withdrawals += withdrawal
            cumulative += flow.signed_amount
            points.append(PatrimonyPoint(flow.datetime, contribution, withdrawal, flow.signed_amount, cumulative))
        return cls(tuple(points), contributions, withdrawals, contributions - withdrawals)
