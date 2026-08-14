from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    datetime: datetime
    total_value: Decimal
    cash: Decimal
    invested_cost: Decimal
    market_value: Decimal
    realized_gain_loss: Decimal
    unrealized_gain_loss: Decimal
    equity_value: Decimal
    fixed_income_value: Decimal
    gold_value: Decimal
    crypto_value: Decimal
