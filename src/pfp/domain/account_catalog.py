from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccountDefinition:
    account_id: str
    name: str
    broker: str
    currency: str = "EUR"


class AccountCatalog:
    """Stable definitions for accounts known by the application."""

    TRADE_REPUBLIC = "Trade Republic"
    ABANCA_AHORRO = "ABANCA_AHORRO"

    _DEFAULTS = (
        AccountDefinition(TRADE_REPUBLIC, "Trade Republic", "Trade Republic"),
        AccountDefinition(ABANCA_AHORRO, "ABANCA ahorro", "ABANCA_AHORRO"),
    )

    @classmethod
    def defaults(cls) -> tuple[AccountDefinition, ...]:
        return cls._DEFAULTS

    @classmethod
    def get(cls, account_id: str) -> AccountDefinition:
        for account in cls._DEFAULTS:
            if account.account_id == account_id:
                return account
        raise ValueError(f"Unknown account: {account_id}")

    @classmethod
    def contains(cls, account_id: str) -> bool:
        return any(account.account_id == account_id for account in cls._DEFAULTS)
