from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_reconciliation import AccountReconciliation
from pfp.domain.portfolio import Portfolio


class AccountReconciliationEngine:
    @staticmethod
    def reconcile(account: Account, expected_balance: Decimal) -> AccountReconciliation:
        return AccountReconciliation(
            account_id=account.id,
            expected_balance=Decimal(str(expected_balance)),
            calculated_balance=account.balance,
        )

    @classmethod
    def reconcile_portfolio(
        cls,
        portfolio: Portfolio,
        expected_balances: dict[str, Decimal],
    ) -> list[AccountReconciliation]:
        accounts_by_id = {account.id: account for account in portfolio.accounts}
        unknown_accounts = set(expected_balances) - set(accounts_by_id)
        if unknown_accounts:
            raise ValueError(
                f"Expected balance provided for unknown account: {sorted(unknown_accounts)[0]}"
            )

        return [
            cls.reconcile(account, expected_balances[account.id])
            for account in portfolio.accounts
            if account.id in expected_balances
        ]
