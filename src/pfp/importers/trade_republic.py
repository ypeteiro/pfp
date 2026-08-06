from decimal import Decimal
from pathlib import Path

import pandas as pd

from pfp.domain.movement import Movement

from .base import Importer


def dec(value):

    if pd.isna(value):
        return Decimal("0")

    return Decimal(str(value))


class TradeRepublicImporter(Importer):

    def load(self, path: Path):

        df = pd.read_csv(path)

        print(df.shape)
        print(df["type"].value_counts())

        movements = []

        for _, row in df.iterrows():

            movement = Movement(

                transaction_id=row["transaction_id"],

                timestamp=pd.to_datetime(row["datetime"]),

                category=row["category"],

                type=row["type"],

                asset_class=row["asset_class"],

                name=row["name"],

                symbol=row["symbol"],

                shares=dec(row["shares"]),

                price=dec(row["price"]),

                amount=dec(row["amount"]),

                fee=dec(row["fee"]),

                tax=dec(row["tax"]),

                currency=row["currency"],

                description=row["description"],

            )

            movements.append(movement)

        return movements