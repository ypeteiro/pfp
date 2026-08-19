import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.account_transfer import AccountTransfer


class AccountTransferRepository:
    def __init__(self, path):
        self.path = Path(path) if path is not None else None

    def load(self):
        if self.path is None or not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [
                AccountTransfer(
                    datetime=datetime.fromisoformat(row["datetime"]),
                    source_account=row["source_account"],
                    destination_account=row["destination_account"],
                    amount=Decimal(row["amount"]),
                    currency=row.get("currency", "EUR"),
                )
                for row in reader
            ]
