from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountReconciliationRecord:
    datetime: datetime
    account_id: str
    expected_balance: Decimal
    calculated_balance: Decimal
    difference: Decimal
    status: str
