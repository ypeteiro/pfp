from dataclasses import dataclass
from decimal import Decimal

from pfp.config import load_target_allocation


TARGET_ALLOCATION = load_target_allocation()


@dataclass(frozen=True, slots=True)
class InvestmentOrder:
    symbol: str
    asset_name: str
    portfolio_class: str
    amount: Decimal


@dataclass(frozen=True, slots=True)
class AllocationRecommendation:
    portfolio_class: str
    amount: Decimal
    current_percent: Decimal
    target_percent: Decimal
    difference_percent: Decimal
    symbol: str | None = None
    asset_name: str | None = None


@dataclass(frozen=True, slots=True)
class Recommendation:
    total_amount: Decimal
    allocations: tuple[AllocationRecommendation, ...]
    orders: tuple[InvestmentOrder, ...]


class RecommendationEngine:

    def __init__(self, target_allocation=None):
        self.target_allocation = (
            target_allocation.copy()
            if target_allocation is not None
            else TARGET_ALLOCATION.copy()
        )

    def recommend(self, portfolio, amount):
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        totals = {
            portfolio_class: Decimal("0")
            for portfolio_class in self.target_allocation
        }

        positions_by_class = {
            portfolio_class: []
            for portfolio_class in self.target_allocation
        }

        for position in portfolio.positions.values():

            portfolio_class = getattr(
                position,
                "portfolio_class",
                None,
            )

            if portfolio_class not in totals:
                continue

            totals[portfolio_class] += position.invested

            positions_by_class[
                portfolio_class
            ].append(position)

        total_invested = sum(totals.values())

        if total_invested <= 0:
            raise ValueError(
                "Portfolio has no classified investments"
            )

        current_percentages = {
            portfolio_class: (
                value
                / total_invested
                * Decimal("100")
            )
            for portfolio_class, value in totals.items()
        }

        projected_total = total_invested + amount

        deficits = {}

        for portfolio_class, target_percent in (
            self.target_allocation.items()
        ):

            target_value = (
                projected_total
                * target_percent
                / Decimal("100")
            )

            deficit = (
                target_value
                - totals[portfolio_class]
            )

            if deficit > 0:
                deficits[portfolio_class] = deficit

        if not deficits:

            allocations = {
                portfolio_class: (
                    amount
                    * target
                    / Decimal("100")
                )
                for portfolio_class, target in (
                    self.target_allocation.items()
                )
            }

        else:

            total_deficit = sum(
                deficits.values()
            )

            allocations = {
                portfolio_class: (
                    amount
                    * deficit
                    / total_deficit
                )
                for portfolio_class, deficit in (
                    deficits.items()
                )
            }

            for portfolio_class in self.target_allocation:

                if portfolio_class not in allocations:
                    allocations[portfolio_class] = Decimal("0")

        allocated = sum(allocations.values())
        remainder = amount - allocated

        if remainder != 0:

            largest_class = max(
                allocations,
                key=allocations.get,
            )

            allocations[largest_class] += remainder

        recommendations = []
        orders = []

        for portfolio_class in self.target_allocation:

            positions = positions_by_class[
                portfolio_class
            ]

            selected_position = None

            if positions:

                selected_position = max(
                    positions,
                    key=lambda position: position.invested,
                )

            allocation_amount = allocations[
                portfolio_class
            ]

            symbol = (
                selected_position.symbol
                if selected_position is not None
                else None
            )

            asset_name = (
                selected_position.name
                if selected_position is not None
                else None
            )

            recommendations.append(
                AllocationRecommendation(
                    portfolio_class=portfolio_class,
                    amount=allocation_amount,
                    current_percent=current_percentages[
                        portfolio_class
                    ],
                    target_percent=self.target_allocation[
                        portfolio_class
                    ],
                    difference_percent=(
                        self.target_allocation[
                            portfolio_class
                        ]
                        - current_percentages[
                            portfolio_class
                        ]
                    ),
                    symbol=symbol,
                    asset_name=asset_name,
                )
            )

            if (
                allocation_amount > 0
                and selected_position is not None
            ):

                orders.append(
                    InvestmentOrder(
                        symbol=selected_position.symbol,
                        asset_name=selected_position.name,
                        portfolio_class=portfolio_class,
                        amount=allocation_amount,
                    )
                )

        return Recommendation(
            total_amount=amount,
            allocations=tuple(recommendations),
            orders=tuple(orders),
        )
