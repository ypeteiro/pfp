from datetime import datetime, timezone
from decimal import Decimal

from pfp.cli import main
from pfp.domain.account_reconciliation_record import AccountReconciliationRecord
from pfp.importers.account_reconciliation_repository import AccountReconciliationRepository


def test_reconcile_history_prints_account_history(tmp_path, capsys):
    history_file = tmp_path / "history.csv"
    repository = AccountReconciliationRepository(history_file)
    repository.save(
        AccountReconciliationRecord(
            datetime=datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc),
            account_id="Trade Republic",
            expected_balance=Decimal("3040.29"),
            calculated_balance=Decimal("3040.29"),
            difference=Decimal("0.00"),
            status="RECONCILED",
        )
    )
    repository.save(
        AccountReconciliationRecord(
            datetime=datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc),
            account_id="Trade Republic",
            expected_balance=Decimal("3240.29"),
            calculated_balance=Decimal("3040.29"),
            difference=Decimal("-200.00"),
            status="MISMATCH",
        )
    )

    main(["reconcile-history", "Trade Republic", "--history-file", str(history_file)])

    output = capsys.readouterr().out
    assert "HISTORIAL DE CONCILIACIÓN" in output
    assert "Trade Republic" in output
    assert "3040.29" in output
    assert "-200.00" in output
    assert "RECONCILED" in output
    assert "MISMATCH" in output


def test_reconcile_history_prints_no_records_for_unknown_account(tmp_path, capsys):
    history_file = tmp_path / "history.csv"

    main(["reconcile-history", "ABANCA", "--history-file", str(history_file)])

    output = capsys.readouterr().out
    assert "No hay registros de conciliación para ABANCA." in output
