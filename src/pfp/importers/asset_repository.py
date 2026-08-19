import csv
from pathlib import Path

from pfp.domain.asset import Asset


class AssetRepository:
    FIELDNAMES = ("symbol", "name", "portfolio_class", "isin", "ticker")

    def __init__(self, path):
        self.path = Path(path)

    def load(self) -> list[Asset]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8", newline="") as file:
            return [
                Asset(
                    symbol=row["symbol"],
                    name=row["name"],
                    portfolio_class=row["portfolio_class"],
                    isin=row.get("isin") or None,
                    ticker=row.get("ticker") or None,
                )
                for row in csv.DictReader(file)
            ]

    def save(self, asset: Asset) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        assets = {existing.symbol: existing for existing in self.load()}
        assets[asset.symbol] = asset
        with self.path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for item in assets.values():
                writer.writerow({
                    "symbol": item.symbol,
                    "name": item.name,
                    "portfolio_class": item.portfolio_class,
                    "isin": item.isin or "",
                    "ticker": item.ticker or "",
                })
