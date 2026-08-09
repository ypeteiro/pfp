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
    )

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []

        investments = []

        with self.path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                investments.append(
                    Investment(
                        datetime=datetime.fromisoformat(
                            row["datetime"]
                        ),
                        symbol=row["symbol"],
                        shares=Decimal(
                            row["shares"]
                        ),
                        amount=Decimal(
                            row["amount"]
                        ),
                        price=Decimal(
                            row["price"]
                        ),
                        portfolio_class=row[
                            "portfolio_class"
                        ],
                        broker=row["broker"],
                    )
                )

        return investments

    def save(self, investment):
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_exists = self.path.exists()

        with self.path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "datetime": (
                        investment.datetime.isoformat()
                    ),
                    "symbol": investment.symbol,
                    "shares": str(
                        investment.shares
                    ),
                    "amount": str(
                        investment.amount
                    ),
                    "price": str(
                        investment.price
                    ),
                    "portfolio_class": (
                        investment.portfolio_class
                    ),
                    "broker": investment.broker,
                }
            )