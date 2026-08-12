import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pfp.domain.snapshot import PortfolioSnapshot


class SnapshotRepository:
    FIELDNAMES = (
        "datetime",
        "total_value",
        "cash",
        "invested_cost",
        "market_value",
        "realized_gain_loss",
        "unrealized_gain_loss",
        "equity_value",
        "fixed_income_value",
        "gold_value",
        "crypto_value",
    )

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [
                PortfolioSnapshot(
                    datetime=datetime.fromisoformat(row["datetime"]),
                    total_value=Decimal(row["total_value"]),
                    cash=Decimal(row["cash"]),
                    invested_cost=Decimal(row["invested_cost"]),
                    market_value=Decimal(row["market_value"]),
                    realized_gain_loss=Decimal(row["realized_gain_loss"]),
                    unrealized_gain_loss=Decimal(row["unrealized_gain_loss"]),
                    equity_value=Decimal(row["equity_value"]),
                    fixed_income_value=Decimal(row["fixed_income_value"]),
                    gold_value=Decimal(row["gold_value"]),
                    crypto_value=Decimal(row["crypto_value"]),
                )
                for row in reader
            ]

    def save(self, snapshot):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            if self.path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(
                {
                    "datetime": snapshot.datetime.isoformat(),
                    "total_value": str(snapshot.total_value),
                    "cash": str(snapshot.cash),
                    "invested_cost": str(snapshot.invested_cost),
                    "market_value": str(snapshot.market_value),
                    "realized_gain_loss": str(snapshot.realized_gain_loss),
                    "unrealized_gain_loss": str(snapshot.unrealized_gain_loss),
                    "equity_value": str(snapshot.equity_value),
                    "fixed_income_value": str(snapshot.fixed_income_value),
                    "gold_value": str(snapshot.gold_value),
                    "crypto_value": str(snapshot.crypto_value),
                }
            )
