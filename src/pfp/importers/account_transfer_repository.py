import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.account_transfer import AccountTransfer


class AccountTransferRepository:
    HEADER = ["datetime", "source_account", "destination_account", "amount", "currency"]

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

    def save(self, transfer):
        if self.path is None:
            raise ValueError("Account transfer path is required")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.path.exists()

        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADER)
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "datetime": transfer.datetime.isoformat(),
                    "source_account": transfer.source_account,
                    "destination_account": transfer.destination_account,
                    "amount": str(transfer.amount),
                    "currency": transfer.currency,
                }
            )
