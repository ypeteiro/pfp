from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from pfp.domain.account_opening_balance import AccountOpeningBalance
from pfp.domain.account_transfer import AccountTransfer
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("tests/fixtures/trade_republic.csv")


def test_trade_republic_rebuild_with_external_account_and_transfer_preserves_totals():
    movements = TradeRepublicImporter().load(CSV_FILE)
    opening_balances = [
        AccountOpeningBalance(
            account_id="ABANCA_AHORRO",
            date=date(2026, 7, 29),
            amount=Decimal("1000"),
        )
    ]
    transfers = [
        AccountTransfer(
            datetime=datetime(2026, 7, 30, tzinfo=timezone.utc),
            source_account="ABANCA_AHORRO",
            destination_account="Trade Republic",
            amount=Decimal("800"),
            currency="EUR",
        )
    ]

    portfolio = PortfolioEngine().build(
        movements,
        opening_balances=opening_balances,
        account_transfers=transfers,
    )

    accounts = {account.account_id: account for account in portfolio.accounts}

    assert set(accounts) == {"ABANCA_AHORRO", "Trade Republic"}
    assert accounts["ABANCA_AHORRO"].balance == Decimal("200")
    assert accounts["Trade Republic"].balance == Decimal("4393.39")
    assert portfolio.cash == Decimal("4593.39")
    assert portfolio.invested == Decimal("21406.61")
    assert portfolio.cash + portfolio.invested == Decimal("26000")

    assert set(portfolio.account_positions["Trade Republic"]) == {
        "BTC",
        "IE00B03HD191",
        "IE00B4L5Y983",
        "IE00B5BMR087",
        "IE00BKM4GZ66",
        "IE00BK5BQT80",
        "IE00BG47KH54",
        "IE00B4ND3602",
        "IE000I1Q42S9",
    }
    assert portfolio.account_positions["ABANCA_AHORRO"] == {}
