from pathlib import Path

from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("tests/fixtures/trade_republic.csv")


def test_import_trade_republic_movements():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    assert len(movements) == 17


def test_import_first_trade_republic_movement():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    movement = movements[0]

    assert movement.transaction_id == "019faf8d-6df2-7457-8c6d-4004d8450c3f"
    assert movement.type == "TRANSFER_INSTANT_INBOUND"
    assert movement.category == "CASH"
    assert movement.currency == "EUR"
    assert movement.amount == 1000
    assert movement.account_type == "DEFAULT"
    
def test_import_movement_has_broker():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    assert movements[0].broker == "Trade Republic"