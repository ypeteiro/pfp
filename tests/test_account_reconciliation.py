from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_reconciliation import AccountReconciliation
from pfp.domain.portfolio import Portfolio
from pfp.engine.account_reconciliation_engine import AccountReconciliationEngine


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


def test_account_reconciliation_engine_uses_account_balance_and_identity():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
        balance=Decimal("3593.39"),
        account_id="TRADE_REPUBLIC",
    )

    reconciliation = AccountReconciliationEngine.reconcile(
        account,
        Decimal("3593.39"),
    )

    assert reconciliation.account_id == "TRADE_REPUBLIC"
    assert reconciliation.expected_balance == Decimal("3593.39")
    assert reconciliation.calculated_balance == Decimal("3593.39")
    assert reconciliation.is_reconciled is True


def test_account_reconciliation_engine_preserves_signed_difference():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
        balance=Decimal("3793.39"),
        account_id="TRADE_REPUBLIC",
    )

    reconciliation = AccountReconciliationEngine.reconcile(
        account,
        Decimal("3593.39"),
    )

    assert reconciliation.difference == Decimal("200")
    assert reconciliation.is_reconciled is False



def test_account_reconciliation_engine_reconciles_all_expected_portfolio_accounts():
    portfolio = Portfolio(accounts=[
        Account(name="ABANCA Ahorro", broker="ABANCA", balance=Decimal("31106"), account_id="ABANCA_AHORRO"),
        Account(name="Trade Republic", broker="Trade Republic", balance=Decimal("3593.39"), account_id="TRADE_REPUBLIC"),
    ])
    reconciliations = AccountReconciliationEngine.reconcile_portfolio(
        portfolio, {"ABANCA_AHORRO": Decimal("31106"), "TRADE_REPUBLIC": Decimal("3593.39")}
    )
    assert [(item.account_id, item.difference, item.is_reconciled) for item in reconciliations] == [
        ("ABANCA_AHORRO", Decimal("0"), True),
        ("TRADE_REPUBLIC", Decimal("0"), True),
    ]


def test_account_reconciliation_engine_rejects_unknown_expected_account():
    portfolio = Portfolio(accounts=[Account(name="Trade Republic", broker="Trade Republic", balance=Decimal("3593.39"), account_id="TRADE_REPUBLIC")])
    try:
        AccountReconciliationEngine.reconcile_portfolio(portfolio, {"MISSING": Decimal("100")})
    except ValueError as exc:
        assert str(exc) == "Expected balance provided for unknown account: MISSING"
    else:
        raise AssertionError("Expected ValueError for unknown account")
