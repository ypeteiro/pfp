from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.portfolio import Portfolio
from pfp.domain.sale import Sale


@dataclass(frozen=True, slots=True)
class RegisterSaleRequest:
    """Validated input for registering one sale order."""

    datetime: datetime
    symbol: str
    shares: Decimal
    amount: Decimal
    price: Decimal
    broker: str = "Trade Republic"
    operation_id: str | None = None
    account_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.datetime, datetime):
            raise ValueError("Sale datetime must be a datetime")
        if not self.symbol.strip():
            raise ValueError("Sale symbol cannot be empty")
        if self.shares <= Decimal("0"):
            raise ValueError("Sale shares must be positive")
        if self.amount <= Decimal("0"):
            raise ValueError("Sale amount must be positive")
        if self.price <= Decimal("0"):
            raise ValueError("Sale price must be positive")
        if not self.broker.strip():
            raise ValueError("Sale broker cannot be empty")
        if self.operation_id is not None and not self.operation_id.strip():
            raise ValueError("Sale operation_id cannot be empty")
        if self.account_id is not None and not self.account_id.strip():
            raise ValueError("Sale account_id cannot be empty")


class RegisterSale:
    """Register a sale through the portfolio domain API."""

    def execute(self, portfolio: Portfolio, request: RegisterSaleRequest) -> Sale:
        sale = Sale(
            datetime=request.datetime,
            symbol=request.symbol,
            shares=request.shares,
            amount=request.amount,
            price=request.price,
            broker=request.broker,
            operation_id=request.operation_id,
            account_id=request.account_id,
        )
        portfolio.add_sale(sale)
        return sale
