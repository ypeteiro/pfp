import csv
from decimal import Decimal


class PriceImporter:

    def load(self, path):

        prices = {}

        with open(
            path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                symbol = row["symbol"].strip()

                if not symbol:
                    continue

                price = Decimal(row["price"])

                if price <= 0:
                    continue

                prices[symbol] = price

        return prices