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
        capital = self.cumulative_capital_flow
        if capital == 0:
            return Decimal("0")
        return self.total_performance / capital * Decimal("100")


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

            performance_percent = (
                performance / cumulative_flow * Decimal("100")
                if cumulative_flow != 0
                else Decimal("0")
            )

            points.append(
                HistoryPoint(
                    snapshot=snapshot,
                    change=change,
                    change_percent=change_percent,
                    capital_flow=period_flow,
                    cumulative_capital_flow=cumulative_flow,
                    performance=performance,
                    performance_percent=performance_percent,
                )
            )
            previous_value = snapshot.total_value
            previous_snapshot_date = snapshot_date

        return History(points=tuple(points))
