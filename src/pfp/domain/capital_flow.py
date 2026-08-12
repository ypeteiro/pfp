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

    @property
    def signed_amount(self) -> Decimal:
        if self.flow_type == FlowType.CONTRIBUTION:
            return self.amount
        return -self.amount
