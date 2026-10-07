"""Historical portfolio value reconstruction."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
        uses_raw_movements = bool(ordered_movements)

        prefetch = getattr(provider, "prefetch", None)
        if prefetch is not None and ordered_dates:
            symbols = {
                item.symbol
                for item in (*ordered_movements, *ordered_investments, *ordered_sales)
                if getattr(item, "symbol", None)
            }
            prefetch(symbols, ordered_dates)

        # The old implementation rebuilt the whole portfolio from scratch for
        # every date. With a long transaction history that became the dominant
        # cost. Replay the ordered events once and only advance cursors as dates
        # move forward.
        engine = PortfolioEngine()
        historical_portfolio = engine.initialize_incremental(ordered_movements) if uses_raw_movements else None
        movement_index = investment_index = sales_index = 0

        for date in ordered_dates:
            if uses_raw_movements:
                while movement_index < len(ordered_movements) and _normalize_datetime(ordered_movements[movement_index].datetime) <= date:
                    engine.apply_movement(historical_portfolio, ordered_movements[movement_index])
                    movement_index += 1

                while investment_index < len(ordered_investments) and _normalize_datetime(ordered_investments[investment_index].datetime) <= date:
                    engine.apply_investment(historical_portfolio, ordered_investments[investment_index])
                    investment_index += 1

                while sales_index < len(ordered_sales) and _normalize_datetime(ordered_sales[sales_index].datetime) <= date:
                    engine.apply_sale(historical_portfolio, ordered_sales[sales_index])
                    sales_index += 1

                historical_portfolio.invested = sum(
                    position.invested for position in historical_portfolio.positions.values()
                )
                for position in historical_portfolio.positions.values():
                    position.validate()

                cash = opening_cash + sum(
                    (
                        movement.amount
                        for movement in ordered_external
                        if movement.account_id != "Trade Republic"
                        and _normalize_datetime(movement.datetime) <= date
                    ),
                    Decimal("0"),
                ) + sum((account.balance for account in historical_portfolio.accounts), Decimal("0"))
                invested_cost = historical_portfolio.invested
                holdings = historical_portfolio.positions
            else:
                cash = opening_cash
                cumulative_invested = Decimal("0")
                holdings: dict[str, Decimal] = {}
                while investment_index < len(ordered_investments) and _normalize_datetime(ordered_investments[investment_index].datetime) <= date:
                    investment = ordered_investments[investment_index]
                    cash -= investment.amount
                    holdings[investment.symbol] = holdings.get(investment.symbol, Decimal("0")) + investment.shares
                    cumulative_invested += investment.amount
                    investment_index += 1
                while sales_index < len(ordered_sales) and _normalize_datetime(ordered_sales[sales_index].datetime) <= date:
                    sale = ordered_sales[sales_index]
                    cash += sale.amount
                    holdings[sale.symbol] = holdings.get(sale.symbol, Decimal("0")) - sale.shares
                    cumulative_invested -= sale.amount
                    sales_index += 1
                for movement in ordered_external:
                    if _normalize_datetime(movement.datetime) <= date:
                        cash += movement.amount
                invested_cost = cumulative_invested

            cumulative_contributed = Decimal("0")
            for flow in ordered_capital:
                if _normalize_datetime(flow.datetime) <= date:
                    cumulative_contributed += flow.amount

            market_value = Decimal("0")
            for symbol, position in holdings.items():
                price = provider.price(symbol, date)
                if price is not None and price.is_finite():
                    shares = position.shares if hasattr(position, "shares") else position
                    market_value += shares * price

            patrimony = cash + market_value
            initial_wealth = opening_cash if uses_raw_movements else Decimal("0")
            snapshots.append(
                PatrimonySnapshot(
                    datetime=date,
                    cash=cash,
                    invested_cost=invested_cost,
                    market_value=market_value,
                    patrimony=patrimony,
                    cumulative_contributed=cumulative_contributed,
                    investment_gain=patrimony - initial_wealth - cumulative_contributed,
                )
            )

        if uses_raw_movements and snapshots:
            first = snapshots[0]
            snapshots.insert(
                0,
                PatrimonySnapshot(
                    datetime=first.datetime - timedelta(days=1),
                    cash=Decimal("0"),
                    invested_cost=Decimal("0"),
                    market_value=Decimal("0"),
                    patrimony=Decimal("0"),
                    cumulative_contributed=Decimal("0"),
                    investment_gain=Decimal("0"),
                ),
            )

        return tuple(snapshots)
