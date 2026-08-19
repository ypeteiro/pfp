from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountTransfer:
    datetime: datetime
    source_account: str
    destination_account: str
    amount: Decimal
    currency: str
