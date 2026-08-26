"""Historical portfolio value reconstruction."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.domain.investment import Investment
from pfp.domain.sale import Sale
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
    """Reconstructs portfolio state at supplied historical dates."""

    @classmethod
    def build(
        cls,
        dates: list[datetime] | tuple[datetime, ...],
        *,
        opening_cash: Decimal = Decimal("0"),
        external_cash_movements: list[ExternalCashMovement] | tuple[ExternalCashMovement, ...] = (),
        capital_movements: list[ExternalCashMovement] | tuple[ExternalCashMovement, ...] | None = None,
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
        snapshots: list[PatrimonySnapshot] = []

        for date in ordered_dates:
            cash = opening_cash
            contributed = Decimal("0")
            holdings: dict[str, Decimal] = {}
            invested_cost = Decimal("0")

            for movement in external_cash_movements:
                if _normalize_datetime(movement.datetime) <= date:
                    cash += movement.amount

            for movement in capital_movements:
                if _normalize_datetime(movement.datetime) <= date:
                    contributed += movement.amount

            for transfer in account_transfers:
                if _normalize_datetime(transfer.datetime) <= date:
                    # Internal transfers redistribute existing cash and therefore
                    # must not affect consolidated cash or cumulative contributions.
                    pass

            for investment in investments:
                if _normalize_datetime(investment.datetime) <= date:
                    cash -= investment.amount
                    holdings[investment.symbol] = holdings.get(investment.symbol, Decimal("0")) + investment.shares
                    invested_cost += investment.amount

            for sale in sales:
                if _normalize_datetime(sale.datetime) <= date:
                    cash += sale.amount
                    holdings[sale.symbol] = holdings.get(sale.symbol, Decimal("0")) - sale.shares
                    invested_cost -= sale.amount

            market_value = Decimal("0")
            for symbol, shares in holdings.items():
                price = provider.price(symbol, date)
                if price is not None:
                    market_value += shares * price

            patrimony = cash + market_value
            snapshots.append(
                PatrimonySnapshot(
                    date,
                    cash,
                    invested_cost,
                    market_value,
                    patrimony,
                    contributed,
                    patrimony - contributed,
                )
            )

        return tuple(snapshots)
