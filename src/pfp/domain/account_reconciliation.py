from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountReconciliation:
    account_id: str
    expected_balance: Decimal
    calculated_balance: Decimal

    @property
    def difference(self) -> Decimal:
        return self.calculated_balance - self.expected_balance

    @property
    def is_reconciled(self) -> bool:
        return self.difference == Decimal("0")
