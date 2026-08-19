from pathlib import Path

import pandas as pd
import pytest

from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.importers.validation import ImportValidationError


CSV_FILE = Path("tests/fixtures/trade_republic.csv")


def test_valid_trade_republic_file_passes_import_validation():
    movements = TradeRepublicImporter().load(CSV_FILE)
    assert len(movements) == 17


def test_import_rejects_duplicate_transaction_ids(tmp_path: Path):
    df = pd.read_csv(CSV_FILE)
    df.loc[1, "transaction_id"] = df.loc[0, "transaction_id"]
    path = tmp_path / "duplicate.csv"
    df.to_csv(path, index=False)

    with pytest.raises(ImportValidationError, match="Identificador duplicado"):
        TradeRepublicImporter().load(path)


def test_import_rejects_invalid_currency(tmp_path: Path):
    df = pd.read_csv(CSV_FILE)
    df.loc[0, "currency"] = "EURO"
    path = tmp_path / "currency.csv"
    df.to_csv(path, index=False)

    with pytest.raises(ImportValidationError, match="Divisa inválida"):
        TradeRepublicImporter().load(path)
