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
                )
                for row in reader
            ]

    def save(self, sale):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.path.exists()

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
                }
            )
