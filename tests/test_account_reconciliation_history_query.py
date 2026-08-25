from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_reconciliation_record import AccountReconciliationRecord
from pfp.importers.account_reconciliation_repository import AccountReconciliationRepository


def record(account_id, timestamp, status="RECONCILED"):
    return AccountReconciliationRecord(
        datetime=datetime.fromisoformat(timestamp),
        account_id=account_id,
        expected_balance=Decimal("100"),
        calculated_balance=Decimal("100"),
        difference=Decimal("0"),
        status=status,
    )


def test_history_returns_records_for_account_in_chronological_order(tmp_path):
    repository = AccountReconciliationRepository(tmp_path / "history.csv")
    repository.save(record("Trade Republic", "2026-08-25T10:00:00+00:00"))
    repository.save(record("ABANCA", "2026-08-25T11:00:00+00:00"))
    repository.save(record("Trade Republic", "2026-08-25T12:00:00+00:00", "MISMATCH"))

    history = repository.history("Trade Republic")

    assert [item.account_id for item in history] == ["Trade Republic", "Trade Republic"]
    assert [item.datetime for item in history] == [
        datetime(2026, 8, 25, 10, tzinfo=timezone.utc),
        datetime(2026, 8, 25, 12, tzinfo=timezone.utc),
    ]


def test_history_returns_empty_list_for_unknown_account(tmp_path):
    repository = AccountReconciliationRepository(tmp_path / "history.csv")
    repository.save(record("Trade Republic", "2026-08-25T10:00:00+00:00"))

    assert repository.history("ABANCA") == []
