"""Historical portfolio value reconstruction for dashboard charts."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.reporting.historical_prices import HistoricalPriceProvider, MappingHistoricalPriceProvider


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


@dataclass(frozen=True, slots=True)
class PatrimonySnapshot:
    datetime: datetime
    cash: Decimal
    invested_cost: Decimal
    market_value: Decimal
    patrimony: Decimal
    cumulative_contributed: Decimal
    investment_gain: Decimal


class PatrimonyHistory:
    """Reconstruct portfolio value at the supplied historical dates."""

    @classmethod
    def build(
        cls,
        dates: list[datetime] | tuple[datetime, ...],
        *,
        movements=(),
        investments=(),
        sales=(),
        capital_flows=(),
        prices: dict[datetime, dict[str, Decimal]] | None = None,
        price_provider: HistoricalPriceProvider | None = None,
    ) -> tuple[PatrimonySnapshot, ...]:
        if prices is not None and price_provider is not None:
            raise ValueError("Provide either prices or price_provider, not both")
        provider = price_provider or MappingHistoricalPriceProvider(prices or {})
        ordered_dates = sorted({_normalize_datetime(value) for value in dates})
        ordered_movements = tuple(sorted(movements, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_investments = tuple(sorted(investments, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_sales = tuple(sorted(sales, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_flows = tuple(sorted(capital_flows, key=lambda item: _normalize_datetime(item.datetime)))
        snapshots: list[PatrimonySnapshot] = []

        for date in ordered_dates:
            applicable_movements = tuple(
                movement for movement in ordered_movements
                if _normalize_datetime(movement.datetime) <= date
            )
            applicable_investments = tuple(
                investment for investment in ordered_investments
                if _normalize_datetime(investment.datetime) <= date
            )
            applicable_sales = tuple(
                sale for sale in ordered_sales
                if _normalize_datetime(sale.datetime) <= date
            )
            portfolio = PortfolioEngine().build(
                list(applicable_movements),
                investments=list(applicable_investments),
                sales=list(applicable_sales),
            )

            market_value = Decimal("0")
            for symbol, position in portfolio.positions.items():
                price = provider.price(symbol, date)
                if price is not None:
                    market_value += position.shares * price

            cumulative_contributed = Decimal("0")
            for flow in ordered_flows:
                if _normalize_datetime(flow.datetime) <= date:
                    cumulative_contributed += flow.signed_amount

            patrimony = portfolio.cash + market_value
            snapshots.append(
                PatrimonySnapshot(
                    datetime=date,
                    cash=portfolio.cash,
                    invested_cost=portfolio.invested,
                    market_value=market_value,
                    patrimony=patrimony,
                    cumulative_contributed=cumulative_contributed,
                    investment_gain=patrimony - cumulative_contributed,
                )
            )

        return tuple(snapshots)
