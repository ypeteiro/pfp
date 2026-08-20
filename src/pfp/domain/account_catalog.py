from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccountDefinition:
    account_id: str
    name: str
    broker: str
    currency: str = "EUR"


TRADE_REPUBLIC_ACCOUNT = AccountDefinition(
    account_id="Trade Republic",
    name="Trade Republic",
    broker="Trade Republic",
)

ABANCA_AHORRO_ACCOUNT = AccountDefinition(
    account_id="ABANCA_AHORRO",
    name="ABANCA Ahorro",
    broker="ABANCA_AHORRO",
)


class AccountCatalog:
    def __init__(self, accounts=None):
        definitions = tuple(accounts or (
            TRADE_REPUBLIC_ACCOUNT,
            ABANCA_AHORRO_ACCOUNT,
        ))
        if not definitions:
            raise ValueError("Account catalog cannot be empty")
        ids = [account.account_id for account in definitions]
        if len(ids) != len(set(ids)):
            raise ValueError("Account ids must be unique")
        self._accounts = {account.account_id: account for account in definitions}

    def get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError as exc:
            raise ValueError(f"Unknown account: {account_id}") from exc

    def contains(self, account_id):
        return account_id in self._accounts

    def all(self):
        return tuple(self._accounts.values())


DEFAULT_ACCOUNT_CATALOG = AccountCatalog()
