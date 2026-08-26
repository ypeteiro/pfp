from decimal import Decimal

from pfp.reporting.portfolio_report import AccountReport, PortfolioReport
from pfp.web.accounts_ui import accounts_html


def test_accounts_page_exposes_manual_balance_and_transfer_actions():
    report = PortfolioReport(
        cash=Decimal("1200"),
        invested=Decimal("0"),
        market_value=Decimal("0"),
        total_value=Decimal("1200"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("0"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(
            AccountReport("ABANCA", "ABANCA", "EUR", Decimal("1000"), "abanca"),
            AccountReport("Trade Republic", "Trade Republic", "EUR", Decimal("200"), "trade_republic"),
        ),
    )

    html = accounts_html(report)

    assert 'action="/accounts/adjust"' in html
    assert 'name="target_balance"' in html
    assert 'action="/account-transfers"' in html
    assert 'name="source_account"' in html
    assert 'name="destination_account"' in html
