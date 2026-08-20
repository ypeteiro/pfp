from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.portfolio_cli import run_portfolio


def test_run_portfolio_reports_account_rows_and_consolidated_invariants(monkeypatch, capsys):
    first = Position("FIRST", "First", Decimal("2"), Decimal("200"), Decimal("100"), "EQUITY", Decimal("120"))
    second = Position("SECOND", "Second", Decimal("1"), Decimal("100"), Decimal("100"), "GOLD", Decimal("120"))
    portfolio = Portfolio(
        accounts=[
            Account("Savings", "ABANCA", balance=Decimal("100"), account_id="ABANCA_AHORRO"),
            Account("Broker", "Trade Republic", balance=Decimal("300"), account_id="Trade Republic"),
        ],
        positions={"FIRST": first, "SECOND": second},
        account_positions={
            "ABANCA_AHORRO": {"FIRST": first},
            "Trade Republic": {"SECOND": second},
        },
        cash=Decimal("400"),
        invested=Decimal("300"),
    )
    monkeypatch.setattr("pfp.portfolio_cli.load_portfolio", lambda *args, **kwargs: portfolio)

    run_portfolio("movements.csv", "investments.csv", "sales.csv")

    output = capsys.readouterr().out
    assert "ABANCA_AHORRO" in output
    assert "Trade Republic" in output
    assert "400.00 €" in output
    assert "300.00 €" in output
    assert "360.00 €" in output
    assert "760.00 €" in output
