import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.external_cash_movement import ExternalCashMovement


class ExternalCashMovementRepository:
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
