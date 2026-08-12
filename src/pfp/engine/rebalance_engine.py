from dataclasses import dataclass
from decimal import Decimal

from pfp.config import load_target_allocation


TARGET_ALLOCATION = load_target_allocation()


@dataclass(frozen=True, slots=True)
class RebalanceOrder:
    action: str
    symbol: str
    asset_name: str
    portfolio_class: str
    amount: Decimal
    shares: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RebalanceAllocation:
    portfolio_class: str
    current_value: Decimal
    current_percent: Decimal
    target_value: Decimal
    target_percent: Decimal
    difference_value: Decimal
    difference_percent: Decimal


@dataclass(frozen=True, slots=True)
class Rebalance:
    total_value: Decimal
    rebalanceable_value: Decimal
    allocations: tuple[RebalanceAllocation, ...]
    orders: tuple[RebalanceOrder, ...]


class RebalanceEngine:

    def __init__(self, target_allocation=None):
        self.target_allocation = (
            target_allocation.copy()
            if target_allocation is not None
            else TARGET_ALLOCATION.copy()
        )

    def rebalance(self, portfolio):
        class_values = {
            portfolio_class: Decimal("0")
            for portfolio_class in self.target_allocation
        }
        positions_by_class = {
            portfolio_class: []
            for portfolio_class in self.target_allocation
        }
        market_value = portfolio.cash

        for position in portfolio.positions.values():
            if position.market_price is None:
                raise ValueError(
                    f"Market price is not available for {position.symbol}"
                )

            position_value = position.market_value
            market_value += position_value

            portfolio_class = getattr(
                position,
                "portfolio_class",
                None,
            )
            if portfolio_class not in class_values:
                continue

            class_values[portfolio_class] += position_value
            positions_by_class[portfolio_class].append(position)

        rebalanceable_value = portfolio.cash + sum(class_values.values())

        if market_value <= 0:
            raise ValueError("Portfolio has no value to rebalance")
        if rebalanceable_value <= 0:
            raise ValueError("Portfolio has no rebalanceable value")

        allocations = []
        orders = []

        for portfolio_class, target_percent in self.target_allocation.items():
            current_value = class_values[portfolio_class]
            current_percent = (
                current_value / rebalanceable_value * Decimal("100")
            )
            target_value = (
                rebalanceable_value * target_percent / Decimal("100")
            )
            difference_value = target_value - current_value
            difference_percent = target_percent - current_percent

            allocations.append(
                RebalanceAllocation(
                    portfolio_class=portfolio_class,
                    current_value=current_value,
                    current_percent=current_percent,
                    target_value=target_value,
                    target_percent=target_percent,
                    difference_value=difference_value,
                    difference_percent=difference_percent,
                )
            )

            positions = positions_by_class[portfolio_class]
            if not positions or difference_value == 0:
                continue

            selected_position = max(
                positions,
                key=lambda position: position.market_value,
            )

            if difference_value > 0:
                orders.append(
                    RebalanceOrder(
                        action="BUY",
                        symbol=selected_position.symbol,
                        asset_name=selected_position.name,
                        portfolio_class=portfolio_class,
                        amount=difference_value,
                    )
                )
            else:
                amount = abs(difference_value)
                shares = amount / selected_position.market_price
                orders.append(
                    RebalanceOrder(
                        action="SELL",
                        symbol=selected_position.symbol,
                        asset_name=selected_position.name,
                        portfolio_class=portfolio_class,
                        amount=amount,
                        shares=shares,
                    )
                )

        return Rebalance(
            total_value=market_value,
            rebalanceable_value=rebalanceable_value,
            allocations=tuple(allocations),
            orders=tuple(orders),
        )
