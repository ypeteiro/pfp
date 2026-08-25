import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.external_cash_movement import ExternalCashMovement


class ExternalCashMovementRepository:
    HEADER = ["datetime", "account_id", "amount", "currency", "description"]

    def __init__(self, path):
        self.path = Path(path) if path is not None else None

    def load(self):
        if self.path is None or not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8", newline="") as file:
            return [
                ExternalCashMovement(
                    datetime=datetime.fromisoformat(row["datetime"]),
                    account_id=row["account_id"],
                    amount=Decimal(row["amount"]),
                    currency=row.get("currency", "EUR"),
                    description=row.get("description") or None,
                )
                for row in csv.DictReader(file)
            ]

    def save(self, movement):
        if self.path is None:
            raise ValueError("External cash movement path is required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        exists = self.path.exists()
        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADER)
            if not exists:
                writer.writeheader()
            writer.writerow({
                "datetime": movement.datetime.isoformat(),
                "account_id": movement.account_id,
                "amount": str(movement.amount),
                "currency": movement.currency,
                "description": movement.description or "",
            })
