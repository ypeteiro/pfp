from decimal import Decimal

from pfp.domain.account_reconciliation import AccountReconciliation


def test_account_reconciliation_reports_zero_difference_when_balances_match():
    reconciliation = AccountReconciliation(
        account_id="ABANCA_AHORRO",
        expected_balance=Decimal("31106"),
        calculated_balance=Decimal("31106"),
    )

    assert reconciliation.difference == Decimal("0")
    assert reconciliation.is_reconciled is True


def test_account_reconciliation_reports_positive_difference():
    reconciliation = AccountReconciliation(
        account_id="TRADE_REPUBLIC",
        expected_balance=Decimal("3593.39"),
        calculated_balance=Decimal("3793.39"),
    )

    assert reconciliation.difference == Decimal("200")
    assert reconciliation.is_reconciled is False


def test_account_reconciliation_reports_negative_difference():
    reconciliation = AccountReconciliation(
        account_id="TRADE_REPUBLIC",
        expected_balance=Decimal("3593.39"),
        calculated_balance=Decimal("3393.39"),
    )

    assert reconciliation.difference == Decimal("-200")
    assert reconciliation.is_reconciled is False
