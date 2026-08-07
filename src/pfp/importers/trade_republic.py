from pathlib import Path
from decimal import Decimal
from datetime import datetime

import pandas as pd

from pfp.domain.movement import Movement
from pfp.importers.base import Importer


class TradeRepublicImporter(Importer):

    def load(self, path: Path) -> list[Movement]:

        df = pd.read_csv(path)

        movements: list[Movement] = []

        for _, row in df.iterrows():

            movements.append(
                Movement(
                    datetime=datetime.fromisoformat(
                        row["datetime"].replace("Z", "+00:00")
                    ),
                    date=datetime.strptime(
                        row["date"],
                        "%Y-%m-%d",
                    ),
                    account_type=row["account_type"],
                    category=row["category"],
                    type=row["type"],
                    asset_class=row["asset_class"],
                    name=row["name"],
                    symbol=None if pd.isna(row["symbol"]) else row["symbol"],
                    shares=(
                        None
                        if pd.isna(row["shares"])
                        else Decimal(str(row["shares"]))
                    ),
                    price=(
                        None
                        if pd.isna(row["price"])
                        else Decimal(str(row["price"]))
                    ),
                    amount=Decimal(str(row["amount"])),
                    fee=(
                        Decimal("0")
                        if pd.isna(row["fee"])
                        else Decimal(str(row["fee"]))
                    ),
                    tax=(
                        Decimal("0")
                        if pd.isna(row["tax"])
                        else Decimal(str(row["tax"]))
                    ),
                    currency=row["currency"],
                    original_amount=(
                        None
                        if pd.isna(row["original_amount"])
                        else Decimal(str(row["original_amount"]))
                    ),
                    original_currency=(
                        None
                        if pd.isna(row["original_currency"])
                        else row["original_currency"]
                    ),
                    fx_rate=(
                        None
                        if pd.isna(row["fx_rate"])
                        else Decimal(str(row["fx_rate"]))
                    ),
                    description=(
                        None
                        if pd.isna(row["description"])
                        else row["description"]
                    ),
                    transaction_id=row["transaction_id"],
                    counterparty_name=(
                        None
                        if pd.isna(row["counterparty_name"])
                        else row["counterparty_name"]
                    ),
                    counterparty_iban=(
                        None
                        if pd.isna(row["counterparty_iban"])
                        else row["counterparty_iban"]
                    ),
                    payment_reference=(
                        None
                        if pd.isna(row["payment_reference"])
                        else row["payment_reference"]
                    ),
                    mcc_code=(
                        None
                        if pd.isna(row["mcc_code"])
                        else row["mcc_code"]
                    ),
                )
            )

        return movements