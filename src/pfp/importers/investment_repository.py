import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.investment import Investment


class InvestmentRepository:

    FIELDNAMES = (
        "datetime",
        "symbol",
        "shares",
        "amount",
        "price",
        "portfolio_class",
        "broker",
        "operation_id",
        "account_id",
    )

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []

        investments = []
        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                investments.append(
                    Investment(
                        datetime=datetime.fromisoformat(row["datetime"]),
                        symbol=row["symbol"],
                        shares=Decimal(row["shares"]),
                        amount=Decimal(row["amount"]),
                        price=Decimal(row["price"]),
                        portfolio_class=row["portfolio_class"],
                        broker=row["broker"],
                        operation_id=row.get("operation_id") or None,
                        account_id=row.get("account_id") or None,
                    )
                )
        return investments

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
        return any(
            existing.operation_id == operation_id
            for existing in self.load()
        )

    def save(self, investment):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if investment.operation_id is not None:
            if any(existing.operation_id == investment.operation_id for existing in self.load()):
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
                    "datetime": investment.datetime.isoformat(),
                    "symbol": investment.symbol,
                    "shares": str(investment.shares),
                    "amount": str(investment.amount),
                    "price": str(investment.price),
                    "portfolio_class": investment.portfolio_class,
                    "broker": investment.broker,
                    "operation_id": investment.operation_id or "",
                    "account_id": investment.account_id or "",
                }
            )
