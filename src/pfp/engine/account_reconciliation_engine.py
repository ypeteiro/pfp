from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_reconciliation import AccountReconciliation


class AccountReconciliationEngine:
    @staticmethod
    def reconcile(account: Account, expected_balance: Decimal) -> AccountReconciliation:
        return AccountReconciliation(
            account_id=account.id,
            expected_balance=Decimal(str(expected_balance)),
            calculated_balance=account.balance,
        )
