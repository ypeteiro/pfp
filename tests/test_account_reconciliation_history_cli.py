from pathlib import Path
from decimal import Decimal

from pfp.cli import run_reconcile
from pfp.importers.account_reconciliation_repository import AccountReconciliationRepository


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


def test_run_reconcile_persists_history_record(tmp_path):
    expected_file = tmp_path / "expected.csv"
    history_file = tmp_path / "reconciliations.csv"
    expected_file.write_text(
        "account_id,expected_balance\nTrade Republic,3040.29\n",
        encoding="utf-8",
    )

    run_reconcile(MOVEMENTS_FILE, expected_file, history_file=history_file)

    records = AccountReconciliationRepository(history_file).load()

    assert len(records) == 1
    assert records[0].account_id == "Trade Republic"
    assert records[0].expected_balance == Decimal("3040.29")
    assert records[0].calculated_balance == Decimal("2840.29")
    assert records[0].difference == Decimal("-200")
    assert records[0].status == "MISMATCH"
    assert records[0].datetime.tzinfo is not None
    assert records[0].datetime.utcoffset() is not None


def test_run_reconcile_appends_history_for_each_execution(tmp_path):
    expected_file = tmp_path / "expected.csv"
    history_file = tmp_path / "reconciliations.csv"
    expected_file.write_text(
        "account_id,expected_balance\nTrade Republic,2840.29\n",
        encoding="utf-8",
    )

    run_reconcile(MOVEMENTS_FILE, expected_file, history_file=history_file)
    run_reconcile(MOVEMENTS_FILE, expected_file, history_file=history_file)

    records = AccountReconciliationRepository(history_file).load()

    assert len(records) == 2
    assert [record.status for record in records] == ["RECONCILED", "RECONCILED"]
    assert [record.account_id for record in records] == ["Trade Republic", "Trade Republic"]
