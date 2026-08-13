from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class FlowType(str, Enum):
    CONTRIBUTION = "CONTRIBUTION"
    WITHDRAWAL = "WITHDRAWAL"


@dataclass(frozen=True, slots=True)
class CapitalFlow:
    datetime: datetime
    amount: Decimal
    flow_type: FlowType
    transaction_id: str | None = None

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValueError("Capital flow amount must be greater than zero")
        if not isinstance(self.flow_type, FlowType):
            raise ValueError("Capital flow type must be a FlowType")
        if self.transaction_id is not None and not self.transaction_id.strip():
            raise ValueError("Capital flow transaction_id must not be empty")

    @property
    def signed_amount(self) -> Decimal:
        if self.flow_type == FlowType.CONTRIBUTION:
            return self.amount
        return -self.amount
