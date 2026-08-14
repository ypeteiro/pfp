from datetime import datetime
from decimal import Decimal

from pfp.reporting.data_quality import validate_report
from pfp.reporting.portfolio_report import MovementReport, PortfolioReport, PositionReport


def make_report(*movements, cash=Decimal("0"), market_value=Decimal("1000")):
    return PortfolioReport(
        cash=cash,
        invested=Decimal("1000"),
        market_value=market_value,
        total_value=cash + market_value,
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=market_value,
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=movements,
    )


def movement(**changes):
    values = dict(
        datetime=datetime(2026, 8, 1), broker="Trade Republic", category="TRADE", type="BUY",
        asset_class="RV", symbol="EUNL", name="MSCI World", shares=Decimal("1"), price=Decimal("100"),
        amount=Decimal("-100"), fee=Decimal("0"), tax=Decimal("0"), currency="EUR",
        description="Compra", transaction_id="tx-1",
    )
    values.update(changes)
    return MovementReport(**values)


def test_valid_report_has_no_data_quality_issues():
    assert validate_report(make_report(movement())) == ()


def test_validation_detects_duplicate_transaction_ids_and_missing_required_fields():
    issues = validate_report(make_report(movement(), movement(datetime=None, transaction_id="tx-1", currency="")))
    codes = {issue.code for issue in issues}
    assert "DUPLICATE_TRANSACTION_ID" in codes
    assert "MISSING_DATETIME" in codes
    assert "INVALID_CURRENCY" in codes


def test_validation_detects_negative_position_and_cash_values():
    report = make_report(cash=Decimal("-1"), market_value=Decimal("-10"))
    report = PortfolioReport(**{**report.__dict__, "positions": (PositionReport("EUNL", "MSCI World", "RV", Decimal("-1"), Decimal("-100"), Decimal("100"), Decimal("100"), Decimal("-10"), None, Decimal("0")),)}) if hasattr(report, "__dict__") else PortfolioReport(
        cash=report.cash, invested=report.invested, market_value=report.market_value, total_value=report.total_value,
        realized_gain_loss=report.realized_gain_loss, unrealized_gain_loss=report.unrealized_gain_loss,
        equity_value=report.equity_value, fixed_income_value=report.fixed_income_value, gold_value=report.gold_value, crypto_value=report.crypto_value,
        positions=(PositionReport("EUNL", "MSCI World", "RV", Decimal("-1"), Decimal("-100"), Decimal("100"), Decimal("100"), Decimal("-10"), None, Decimal("0")),), accounts=(), movements=(),
    )
    codes = {issue.code for issue in validate_report(report)}
    assert {"NEGATIVE_CASH", "NEGATIVE_MARKET_VALUE", "NEGATIVE_SHARES", "NEGATIVE_INVESTED", "NEGATIVE_POSITION_VALUE"} <= codes
