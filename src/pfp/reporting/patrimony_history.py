"""Historical portfolio value reconstruction."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.domain.investment import Investment
from pfp.domain.sale import Sale
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.reporting.historical_prices import HistoricalPriceProvider, MappingHistoricalPriceProvider


def _normalize_datetime(value: datetime) -> datetime:
    """Use naive UTC datetimes consistently inside historical reporting."""
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
    """Reconstruct portfolio state at the supplied historical dates."""

    @classmethod
    def build(
        cls,
        dates: list[datetime] | tuple[datetime, ...],
        *,
        opening_cash: Decimal = Decimal("0"),
        external_cash_movements: list[ExternalCashMovement] | tuple[ExternalCashMovement, ...] = (),
        capital_movements: list[ExternalCashMovement] | tuple[ExternalCashMovement, ...] | None = None,
        movements=(),
        investments: list[Investment] | tuple[Investment, ...] = (),
        sales: list[Sale] | tuple[Sale, ...] = (),
        account_transfers: list[AccountTransfer] | tuple[AccountTransfer, ...] = (),
        prices: dict[datetime, dict[str, Decimal]] | None = None,
        price_provider: HistoricalPriceProvider | None = None,
    ) -> tuple[PatrimonySnapshot, ...]:
        if prices is not None and price_provider is not None:
            raise ValueError("Provide either prices or price_provider, not both")
        provider = price_provider or MappingHistoricalPriceProvider(prices or {})
        capital_movements = external_cash_movements if capital_movements is None else capital_movements
        if capital_movements is external_cash_movements:
            trade_republic_movements = tuple(
                movement
                for movement in external_cash_movements
                if movement.account_id == "Trade Republic"
            )
            if trade_republic_movements:
                capital_movements = trade_republic_movements

        ordered_dates = sorted({_normalize_datetime(date) for date in dates})
        ordered_movements = tuple(sorted(movements, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_investments = tuple(sorted(investments, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_sales = tuple(sorted(sales, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_external = tuple(sorted(external_cash_movements, key=lambda item: _normalize_datetime(item.datetime)))
        ordered_capital = tuple(sorted(capital_movements, key=lambda item: _normalize_datetime(item.datetime)))
        snapshots: list[PatrimonySnapshot] = []

        for date in ordered_dates:
            applicable_investments = tuple(
                investment for investment in ordered_investments
                if _normalize_datetime(investment.datetime) <= date
            )
            applicable_sales = tuple(
                sale for sale in ordered_sales
                if _normalize_datetime(sale.datetime) <= date
            )

            if ordered_movements:
                applicable_movements = tuple(
                    movement for movement in ordered_movements
                    if _normalize_datetime(movement.datetime) <= date
                )
                historical_portfolio = PortfolioEngine().build(
                    list(applicable_movements),
                    investments=list(applicable_investments),
                    sales=list(applicable_sales),
                )
                cash = opening_cash + sum(
                    (
                        movement.amount
                        for movement in ordered_external
                        if movement.account_id != "Trade Republic"
                        and _normalize_datetime(movement.datetime) <= date
                    ),
                    Decimal("0"),
                ) + historical_portfolio.cash
                invested_cost = historical_portfolio.invested
                holdings = historical_portfolio.positions
            else:
                cash = opening_cash
                cumulative_invested = Decimal("0")
                holdings: dict[str, Decimal] = {}
                for movement in ordered_external:
                    if _normalize_datetime(movement.datetime) <= date:
                        cash += movement.amount
                for investment in applicable_investments:
                    cash -= investment.amount
                    holdings[investment.symbol] = holdings.get(investment.symbol, Decimal("0")) + investment.shares
                    cumulative_invested += investment.amount
                for sale in applicable_sales:
                    cash += sale.amount
                    holdings[sale.symbol] = holdings.get(sale.symbol, Decimal("0")) - sale.shares
                    cumulative_invested -= sale.amount
                invested_cost = cumulative_invested

            cumulative_contributed = Decimal("0")
            for flow in ordered_capital:
                if _normalize_datetime(flow.datetime) <= date:
                    cumulative_contributed += flow.amount

            market_value = Decimal("0")
            if ordered_movements:
                for symbol, position in holdings.items():
                    price = provider.price(symbol, date)
                    if price is not None:
                        market_value += position.shares * price
            else:
                for symbol, shares in holdings.items():
                    price = provider.price(symbol, date)
                    if price is not None:
                        market_value += shares * price

            patrimony = cash + market_value
            snapshots.append(
                PatrimonySnapshot(
                    datetime=date,
                    cash=cash,
                    invested_cost=invested_cost,
                    market_value=market_value,
                    patrimony=patrimony,
                    cumulative_contributed=cumulative_contributed,
                    investment_gain=patrimony - cumulative_contributed,
                )
            )

        return tuple(snapshots)
