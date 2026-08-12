from dataclasses import dataclass
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow
from pfp.domain.snapshot import PortfolioSnapshot


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    snapshot: PortfolioSnapshot
    change: Decimal
    change_percent: Decimal
    capital_flow: Decimal
    cumulative_capital_flow: Decimal
    performance: Decimal
    performance_percent: Decimal
    time_weighted_return: Decimal


@dataclass(frozen=True, slots=True)
class History:
    points: tuple[HistoryPoint, ...]

    @property
    def initial_value(self):
        if not self.points:
            return Decimal("0")
        return self.points[0].snapshot.total_value

    @property
    def current_value(self):
        if not self.points:
            return Decimal("0")
        return self.points[-1].snapshot.total_value

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
        if not self.points:
            return Decimal("0")
        return self.points[-1].cumulative_capital_flow

    @property
    def total_performance(self):
        if not self.points:
            return Decimal("0")
        return self.points[-1].performance

    @property
    def total_performance_percent(self):
        if not self.points:
            return Decimal("0")
        initial_value = self.initial_value
        if initial_value == 0:
            return Decimal("0")
        return self.total_performance / initial_value * Decimal("100")

    @property
    def time_weighted_return(self):
        if not self.points:
            return Decimal("0")
        return self.points[-1].time_weighted_return

    @property
    def time_weighted_return_percent(self):
        return self.time_weighted_return * Decimal("100")


class HistoryEngine:
    def build(self, snapshots, capital_flows=None):
        ordered = sorted(snapshots, key=lambda snapshot: snapshot.datetime)
        flows = sorted(capital_flows or [], key=lambda flow: flow.datetime)
        points = []

        if not ordered:
            return History(points=())

        initial_value = ordered[0].total_value
        previous_value = None
        cumulative_flow = Decimal("0")
        previous_snapshot_date = None
        initial_period_flow = Decimal("0")
        cumulative_twr_factor = Decimal("1")

        for snapshot in ordered:
            if previous_value is None:
                change = Decimal("0")
                change_percent = Decimal("0")
            else:
                change = snapshot.total_value - previous_value
                change_percent = (
                    change / previous_value * Decimal("100")
                    if previous_value != 0
                    else Decimal("0")
                )

            snapshot_date = snapshot.datetime.date()
            if previous_snapshot_date is None:
                period_flow = sum(
                    (
                        flow.signed_amount
                        for flow in flows
                        if flow.datetime.date() <= snapshot_date
                    ),
                    Decimal("0"),
                )
                initial_period_flow = period_flow
            else:
                period_flow = sum(
                    (
                        flow.signed_amount
                        for flow in flows
                        if previous_snapshot_date < flow.datetime.date() <= snapshot_date
                    ),
                    Decimal("0"),
                )

            cumulative_flow += period_flow

            if previous_snapshot_date is None:
                performance = snapshot.total_value - cumulative_flow
            else:
                post_initial_flow = cumulative_flow - initial_period_flow
                performance = snapshot.total_value - initial_value - post_initial_flow

                if previous_value != 0:
                    period_end_ex_flow = snapshot.total_value - period_flow
                    cumulative_twr_factor *= period_end_ex_flow / previous_value

            performance_percent = (
                performance / initial_value * Decimal("100")
                if initial_value != 0
                else Decimal("0")
            )

            time_weighted_return = cumulative_twr_factor - Decimal("1")

            points.append(
                HistoryPoint(
                    snapshot=snapshot,
                    change=change,
                    change_percent=change_percent,
                    capital_flow=period_flow,
                    cumulative_capital_flow=cumulative_flow,
                    performance=performance,
                    performance_percent=performance_percent,
                    time_weighted_return=time_weighted_return,
                )
            )
            previous_value = snapshot.total_value
            previous_snapshot_date = snapshot_date

        return History(points=tuple(points))
