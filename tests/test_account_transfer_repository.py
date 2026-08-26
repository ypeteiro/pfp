from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_transfer import AccountTransfer
from pfp.importers.account_transfer_repository import AccountTransferRepository


def test_load_account_transfers(tmp_path):
    path = tmp_path / "account_transfers.csv"
    path.write_text(
        "datetime,source_account,destination_account,amount,currency\n"
        "2026-08-01T10:30:00+00:00,ABANCA_NOMINA,ABANCA_AHORRO,200.00,EUR\n"
        "2026-08-01T10:31:00+00:00,ABANCA_NOMINA,TRADE_REPUBLIC,800.00,EUR\n",
        encoding="utf-8",
    )

    transfers = AccountTransferRepository(path).load()

    assert len(transfers) == 2
    assert transfers[0].datetime == datetime(2026, 8, 1, 10, 30, tzinfo=timezone.utc)
    assert transfers[0].source_account == "ABANCA_NOMINA"
    assert transfers[0].destination_account == "ABANCA_AHORRO"
    assert transfers[0].amount == Decimal("200.00")
    assert transfers[0].currency == "EUR"


def test_load_missing_account_transfer_file_returns_empty_list(tmp_path):
    assert AccountTransferRepository(tmp_path / "missing.csv").load() == []


def test_load_none_account_transfer_file_returns_empty_list():
    assert AccountTransferRepository(None).load() == []


def test_save_account_transfer(tmp_path):
    path = tmp_path / "account_transfers.csv"
    transfer = AccountTransfer(
        datetime=datetime(2026, 8, 1, 10, 30, tzinfo=timezone.utc),
        source_account="ABANCA_NOMINA",
        destination_account="TRADE_REPUBLIC",
        amount=Decimal("800.00"),
        currency="EUR",
    )

    AccountTransferRepository(path).save(transfer)

    assert path.read_text(encoding="utf-8") == (
        "datetime,source_account,destination_account,amount,currency\n"
        "2026-08-01T10:30:00+00:00,ABANCA_NOMINA,TRADE_REPUBLIC,800.00,EUR\n"
    )


def test_save_account_transfer_appends_without_rewriting_header(tmp_path):
    path = tmp_path / "account_transfers.csv"
    repository = AccountTransferRepository(path)
    transfer = AccountTransfer(
        datetime=datetime(2026, 8, 1, 10, 30, tzinfo=timezone.utc),
        source_account="ABANCA_NOMINA",
        destination_account="TRADE_REPUBLIC",
        amount=Decimal("800.00"),
        currency="EUR",
    )

    repository.save(transfer)
    repository.save(transfer)

    assert path.read_text(encoding="utf-8") == (
        "datetime,source_account,destination_account,amount,currency\n"
        "2026-08-01T10:30:00+00:00,ABANCA_NOMINA,TRADE_REPUBLIC,800.00,EUR\n"
        "2026-08-01T10:30:00+00:00,ABANCA_NOMINA,TRADE_REPUBLIC,800.00,EUR\n"
    )


def test_save_none_account_transfer_file_raises_value_error():
    transfer = AccountTransfer(
        datetime=datetime(2026, 8, 1, 10, 30, tzinfo=timezone.utc),
        source_account="ABANCA_NOMINA",
        destination_account="TRADE_REPUBLIC",
        amount=Decimal("800.00"),
        currency="EUR",
    )

    try:
        AccountTransferRepository(None).save(transfer)
    except ValueError as exc:
        assert str(exc) == "Account transfer path is required"
    else:
        raise AssertionError("Expected ValueError")
