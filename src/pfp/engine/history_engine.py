from dataclasses import dataclass
from decimal import Decimal

from pfp.domain.snapshot import PortfolioSnapshot


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    snapshot: PortfolioSnapshot
    change: Decimal
    change_percent: Decimal


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


class HistoryEngine:
    def build(self, snapshots):
        ordered = sorted(snapshots, key=lambda snapshot: snapshot.datetime)
        points = []
        previous_value = None

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

            points.append(
                HistoryPoint(
                    snapshot=snapshot,
                    change=change,
                    change_percent=change_percent,
                )
            )
            previous_value = snapshot.total_value

        return History(points=tuple(points))
