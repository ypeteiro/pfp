from dataclasses import dataclass
from decimal import Decimal

import pytest

from pfp.domain.account import Account
from pfp.domain.account_reconciliation import AccountReconciliation
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp
from pfp.web.reconciliation_ui import reconciliation_html
from pfp.web.server import parse_reconciliation_request


@dataclass(frozen=True)
class DummyAccount:
    id: str
    balance: Decimal


def report():
    return PortfolioReport(
        cash=Decimal("100"), invested=Decimal("1000"), market_value=Decimal("1000"), total_value=Decimal("1100"),
        realized_gain_loss=Decimal("10"), unrealized_gain_loss=Decimal("20"),
        equity_value=Decimal("750"), fixed_income_value=Decimal("200"), gold_value=Decimal("50"), crypto_value=Decimal("0"),
        positions=(), accounts=(), movements=(),
    )


def test_reconciliation_page_renders_account_and_expected_balance_form():
    accounts = (DummyAccount("Trade Republic", Decimal("3040.29")), DummyAccount("ABANCA", Decimal("200.00")))
    html = WebApp(report(), accounts=accounts).render("/reconciliation")
    assert "Conciliación" in html
    assert 'name="account_id"' in html
    assert 'name="expected_balance"' in html
    assert "Trade Republic" in html
    assert "ABANCA" in html
    assert 'action="/reconcile"' in html


def test_reconciliation_result_is_rendered():
    result = AccountReconciliation("Trade Republic", Decimal("3040.29"), Decimal("3040.29"))
    html = reconciliation_html((DummyAccount("Trade Republic", Decimal("3040.29")),), result=result)
    assert "RECONCILED" in html
    assert "3040.29 €" in html
    assert "0.00 €" in html


def test_parse_reconciliation_request():
    account_id, expected = parse_reconciliation_request({"account_id": ["Trade Republic"], "expected_balance": ["3040.29"]})
    assert account_id == "Trade Republic"
    assert expected == Decimal("3040.29")


def test_parse_reconciliation_request_rejects_negative_balance():
    with pytest.raises(ValueError, match="no puede ser negativo"):
        parse_reconciliation_request({"account_id": ["Trade Republic"], "expected_balance": ["-1"]})
