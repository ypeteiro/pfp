from decimal import Decimal

from pfp.importers.price_importer import PriceImporter


def test_price_importer_loads_prices(tmp_path):

    csv_file = tmp_path / "prices.csv"

    csv_file.write_text(
        "symbol,price,currency\n"
        "BTC,55900,EUR\n"
        "IE00B4L5Y983,142.50,EUR\n",
        encoding="utf-8",
    )

    prices = PriceImporter().load(csv_file)

    assert prices["BTC"] == Decimal("55900")
    assert prices["IE00B4L5Y983"] == Decimal("142.50")