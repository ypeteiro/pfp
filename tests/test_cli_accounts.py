from decimal import Decimal

from pfp.cli import build_parser, run_accounts
from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio


def test_accounts_command_accepts_movements_and_optional_repositories():
    args = build_parser().parse_args(
        [
            "accounts",
            "movements.csv",
            "--investments-file",
            "investments.csv",
            "--sales-file",
            "sales.csv",
        ]
    )

    assert args.command == "accounts"
    assert args.movements_file == "movements.csv"
    assert args.investments_file == "investments.csv"
    assert args.sales_file == "sales.csv"


def test_run_accounts_reports_account_identity_and_reconciled_totals(monkeypatch, capsys):
    portfolio = Portfolio(
        accounts=[
            Account("Savings", "ABANCA", balance=Decimal("700"), account_id="ABANCA_AHORRO"),
            Account("Broker", "Trade Republic", balance=Decimal("300"), account_id="Trade Republic"),
        ],
        cash=Decimal("1000"),
    )
    monkeypatch.setattr("pfp.cli.load_portfolio", lambda *args, **kwargs: portfolio)

    run_accounts("movements.csv", "investments.csv", "sales.csv")

    output = capsys.readouterr().out
    assert "ABANCA_AHORRO" in output
    assert "Trade Republic" in output
    assert "1000.00 €" in output
    assert "0.00 €" in output
