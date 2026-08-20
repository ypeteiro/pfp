import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from pfp.domain.account_opening_balance import AccountOpeningBalance


class AccountOpeningBalanceRepository:
    def __init__(self, path):
        self.path = Path(path) if path is not None else None

    def load(self):
        if self.path is None or not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [
                AccountOpeningBalance(
                    account_id=row["account_id"],
                    date=date.fromisoformat(row["date"]),
                    amount=Decimal(row["amount"]),
                    currency=row.get("currency", "EUR"),
                )
                for row in reader
            ]
