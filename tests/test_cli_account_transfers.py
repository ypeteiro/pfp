from decimal import Decimal
from pathlib import Path

from pfp.cli import load_portfolio


MOVEMENTS_FILE = Path("tests/fixtures/trade_republic_cli.csv")
OPENING_BALANCES_FILE = Path("data/accounts/abanca_ahorro_opening_balance.csv")


def test_load_portfolio_applies_internal_account_transfer(tmp_path):
    transfers_file = tmp_path / "account_transfers.csv"
    transfers_file.write_text(
        "datetime,source_account,destination_account,amount,currency\n"
        "2026-08-01T10:30:00+00:00,ABANCA_AHORRO,Trade Republic,100.00,EUR\n",
        encoding="utf-8",
    )
    portfolio = load_portfolio(MOVEMENTS_FILE, opening_balances_file=OPENING_BALANCES_FILE, account_transfers_file=transfers_file)
    accounts = {account.account_id: account for account in portfolio.accounts}
    assert accounts["ABANCA_AHORRO"].balance == Decimal("31079.70")
    assert accounts["Trade Republic"].balance == Decimal("2940.29")
    assert portfolio.cash == Decimal("34019.99")
