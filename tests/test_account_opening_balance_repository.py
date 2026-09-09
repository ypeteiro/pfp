from decimal import Decimal

from pfp.importers.account_opening_balance_repository import AccountOpeningBalanceRepository


def test_opening_balance_repository_falls_back_to_abanca_filename(tmp_path):
    fallback = tmp_path / "abanca_ahorro_opening_balance.csv"
    fallback.write_text(
        "account_id,date,amount,currency\nABANCA_AHORRO,2026-01-01,31179.70,EUR\n",
        encoding="utf-8",
    )

    balances = AccountOpeningBalanceRepository(tmp_path / "opening_balances.csv").load()

    assert len(balances) == 1
    assert balances[0].account_id == "ABANCA_AHORRO"
    assert balances[0].amount == Decimal("31179.70")
