import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.sale import Sale


class SaleRepository:
    FIELDNAMES = (
        "datetime",
        "symbol",
        "shares",
        "amount",
        "price",
        "broker",
        "operation_id",
        "account_id",
    )

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [
                Sale(
                    datetime=datetime.fromisoformat(row["datetime"]),
                    symbol=row["symbol"],
                    shares=Decimal(row["shares"]),
                    amount=Decimal(row["amount"]),
                    price=Decimal(row["price"]),
                    broker=row["broker"],
                    operation_id=row.get("operation_id") or None,
                    account_id=row.get("account_id") or None,
                )
                for row in reader
            ]

    def _migrate_legacy_header(self):
        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames == list(self.FIELDNAMES):
                return
            rows = list(reader)

        with self.path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for row in rows:
                row["operation_id"] = row.get("operation_id") or ""
                row["account_id"] = row.get("account_id") or ""
                writer.writerow({field: row.get(field, "") for field in self.FIELDNAMES})

    def exists_by_operation_id(self, operation_id: str) -> bool:
        if not operation_id or not operation_id.strip():
            return False
        return any(existing.operation_id == operation_id for existing in self.load())

    def save(self, sale):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if sale.operation_id is not None and self.exists_by_operation_id(sale.operation_id):
            return

        file_exists = self.path.exists()
        if file_exists:
            self._migrate_legacy_header()

        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "datetime": sale.datetime.isoformat(),
                    "symbol": sale.symbol,
                    "shares": str(sale.shares),
                    "amount": str(sale.amount),
                    "price": str(sale.price),
                    "broker": sale.broker,
                    "operation_id": sale.operation_id or "",
                    "account_id": sale.account_id or "",
                }
            )
