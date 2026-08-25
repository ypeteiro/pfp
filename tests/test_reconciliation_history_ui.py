from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.account_reconciliation_record import AccountReconciliationRecord
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp
from pfp.web.reconciliation_history_ui import reconciliation_history_html


def report():
    return PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )


def records():
    return (
        AccountReconciliationRecord(
            datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc),
            "Trade Republic", Decimal("3040.29"), Decimal("3040.29"), Decimal("0"), "RECONCILED",
        ),
        AccountReconciliationRecord(
            datetime(2026, 8, 25, 19, 0, tzinfo=timezone.utc),
            "Trade Republic", Decimal("3040.29"), Decimal("2940.29"), Decimal("-100.00"), "MISMATCH",
        ),
    )


def test_reconciliation_history_renders_records_for_selected_account():
    html = WebApp(report(), reconciliation_history=records()).render("/reconciliation-history?account_id=Trade+Republic")
    assert "Historial de conciliación" in html
    assert "Trade Republic" in html
    assert "2940.29 €" in html
    assert "-100.00 €" in html
    assert "MISMATCH" in html
    assert "3040.29 €" in html


def test_reconciliation_history_shows_empty_state_for_unknown_account():
    html = reconciliation_history_html(records(), "ABANCA")
    assert "No hay registros de conciliación para esta cuenta." in html
    assert "ABANCA" in html


def test_app_navigation_includes_reconciliation_history():
    html = WebApp(report()).render("/reconciliation-history")
    assert 'href="/reconciliation-history"' in html
    assert 'aria-current="page" class="active"' in html
