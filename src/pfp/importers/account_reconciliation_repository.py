import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.account_reconciliation_record import AccountReconciliationRecord


class AccountReconciliationRepository:
    FIELDNAMES = (
        "datetime",
        "account_id",
        "expected_balance",
        "calculated_balance",
        "difference",
        "status",
    )

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [
                AccountReconciliationRecord(
                    datetime=datetime.fromisoformat(row["datetime"]),
                    account_id=row["account_id"],
                    expected_balance=Decimal(row["expected_balance"]),
                    calculated_balance=Decimal(row["calculated_balance"]),
                    difference=Decimal(row["difference"]),
                    status=row["status"],
                )
                for row in reader
            ]

    def save(self, record):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.path.exists()
        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            if not file_exists or self.path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(
                {
                    "datetime": record.datetime.isoformat(),
                    "account_id": record.account_id,
                    "expected_balance": str(record.expected_balance),
                    "calculated_balance": str(record.calculated_balance),
                    "difference": str(record.difference),
                    "status": record.status,
                }
            )
