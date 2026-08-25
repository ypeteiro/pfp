from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_reconciliation_record import AccountReconciliationRecord
from pfp.importers.account_reconciliation_repository import AccountReconciliationRepository


def test_account_reconciliation_repository_saves_and_loads_record(tmp_path):
    path = tmp_path / "reconciliations.csv"
    repository = AccountReconciliationRepository(path)
    record = AccountReconciliationRecord(
        datetime=datetime(2026, 8, 25, 20, 0, tzinfo=timezone.utc),
        account_id="TRADE_REPUBLIC",
        expected_balance=Decimal("3593.39"),
        calculated_balance=Decimal("3793.39"),
        difference=Decimal("200"),
        status="MISMATCH",
    )

    repository.save(record)

    assert repository.load() == [record]


def test_account_reconciliation_repository_appends_history(tmp_path):
    path = tmp_path / "reconciliations.csv"
    repository = AccountReconciliationRepository(path)
    first = AccountReconciliationRecord(
        datetime=datetime(2026, 8, 24, tzinfo=timezone.utc),
        account_id="TRADE_REPUBLIC",
        expected_balance=Decimal("3593.39"),
        calculated_balance=Decimal("3393.39"),
        difference=Decimal("-200"),
        status="MISMATCH",
    )
    second = AccountReconciliationRecord(
        datetime=datetime(2026, 8, 25, tzinfo=timezone.utc),
        account_id="TRADE_REPUBLIC",
        expected_balance=Decimal("3593.39"),
        calculated_balance=Decimal("3593.39"),
        difference=Decimal("0"),
        status="RECONCILED",
    )

    repository.save(first)
    repository.save(second)

    assert repository.load() == [first, second]
