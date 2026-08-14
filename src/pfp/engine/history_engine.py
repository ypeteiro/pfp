from dataclasses import dataclass
from decimal import Decimal, localcontext

from pfp.domain.capital_flow import CapitalFlow
from pfp.domain.snapshot import PortfolioSnapshot
from pfp.engine.xirr_engine import XirrEngine


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    snapshot: PortfolioSnapshot
    change: Decimal
    change_percent: Decimal
    capital_flow: Decimal
    cumulative_capital_flow: Decimal
    performance: Decimal
    performance_percent: Decimal
    time_weighted_return: Decimal | None


@dataclass(frozen=True, slots=True)
class History:
    points: tuple[HistoryPoint, ...]
    xirr: Decimal | None = None

    @property
    def initial_value(self):
        return self.points[0].snapshot.total_value if self.points else Decimal("0")

    @property
    def current_value(self):
        return self.points[-1].snapshot.total_value if self.points else Decimal("0")

    @property
    def total_change(self):
        return self.current_value - self.initial_value

    @property
    def total_change_percent(self):
        if self.initial_value == 0:
            return Decimal("0")
        return self.total_change / self.initial_value * Decimal("100")

    @property
    def cumulative_capital_flow(self):
        return self.points[-1].cumulative_capital_flow if self.points else Decimal("0")

    @property
    def total_performance(self):
        return self.points[-1].performance if self.points else Decimal("0")

    @property
    def total_performance_percent(self):
        if not self.points or self.initial_value == 0:
            return Decimal("0")
        return self.total_performance / self.initial_value * Decimal("100")

    @property
    def time_weighted_return(self):
        return self.points[-1].time_weighted_return if self.points else None

    @property
    def time_weighted_return_percent(self):
        value = self.time_weighted_return
        return None if value is None else value * Decimal("100")

    @property
    def xirr_percent(self):
        return None if self.xirr is None else self.xirr * Decimal("100")


class HistoryEngine:
    def __init__(self, xirr_engine=None):
        self.xirr_engine = xirr_engine or XirrEngine()

    def build(self, snapshots, capital_flows=None):
        ordered = sorted(snapshots, key=lambda snapshot: snapshot.datetime)
        flows = sorted(capital_flows or [], key=lambda flow: flow.datetime)
        if not ordered:
            return History(points=())

        initial_value = ordered[0].total_value
        previous_value = None
        previous_snapshot_datetime = None
        cumulative_flow = Decimal("0")
        cumulative_twr_factor = Decimal("1")
        points = []

        for snapshot in ordered:
            snapshot_date = snapshot.datetime.date()
            if previous_snapshot_datetime is None:
                period_flow = sum(
                    (flow.signed_amount for flow in flows if flow.datetime.date() <= snapshot_date),
                    Decimal("0"),
                )
            else:
                previous_date = previous_snapshot_datetime.date()
                period_flow = sum(
                    (
                        flow.signed_amount
                        for flow in flows
                        if previous_date < flow.datetime.date() <= snapshot_date
                    ),
                    Decimal("0"),
                )

            cumulative_flow += period_flow

            if previous_value is None:
                change = Decimal("0")
                change_percent = Decimal("0")
                performance = snapshot.total_value - cumulative_flow
                twr = None
            else:
                change = snapshot.total_value - previous_value
                change_percent = change / previous_value * Decimal("100") if previous_value else Decimal("0")
                performance = snapshot.total_value - initial_value - cumulative_flow
                with localcontext() as context:
                    context.prec = 40
                    if previous_value:
                        period_factor = (snapshot.total_value - period_flow) / previous_value
                        cumulative_twr_factor *= period_factor
                twr = cumulative_twr_factor - Decimal("1")

            performance_percent = performance / initial_value * Decimal("100") if initial_value else Decimal("0")
            points.append(
                HistoryPoint(
                    snapshot=snapshot,
                    change=change,
                    change_percent=change_percent,
                    capital_flow=period_flow,
                    cumulative_capital_flow=cumulative_flow,
                    performance=performance,
                    performance_percent=performance_percent,
                    time_weighted_return=twr,
                )
            )

            if previous_value is None:
                # Capital already present on the first snapshot date is part of
                # the starting capital, not a return-producing period flow.
                previous_value = snapshot.total_value + period_flow
            else:
                previous_value = snapshot.total_value
            previous_snapshot_datetime = snapshot.datetime

        xirr = self.xirr_engine.calculate(flows, ordered[-1].total_value, ordered[-1].datetime)
        return History(points=tuple(points), xirr=xirr)
