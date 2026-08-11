from decimal import Decimal
from pathlib import Path

from pfp.cli import run_rebalance


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


def _price_provider():
    class StubPriceProvider:
        def get_prices(self, symbols):
            return {
                "IE00BK5BQT80": Decimal("100"),
                "IE00BG47KH54": Decimal("25"),
                "IE00B4ND3602": Decimal("75"),
                "IE00BKM4GZ66": Decimal("46"),
                "IE00B03HD191": Decimal("64"),
                "IE00B4L5Y983": Decimal("129"),
                "IE00B5BMR087": Decimal("724"),
                "IE000I1Q42S9": Decimal("4.34"),
                "BTC": Decimal("55000"),
            }

    return StubPriceProvider()


def test_run_rebalance_prints_market_allocation_and_orders(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    run_rebalance(
        MOVEMENTS_FILE,
        investments_file,
        sales_file,
        price_provider=_price_provider(),
    )

    output = capsys.readouterr().out
    assert "========== REBALANCEO ==========" in output
    assert "## ASIGNACIÓN" in output
    assert "## ÓRDENES" in output
    assert "Comandos ejecutables:" in output


def test_run_rebalance_execute_persists_orders(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    run_rebalance(
        MOVEMENTS_FILE,
        investments_file,
        sales_file,
        price_provider=_price_provider(),
        execute=True,
    )

    output = capsys.readouterr().out
    assert "Rebalanceo ejecutado y persistido." in output

    investments = investments_file.read_text(encoding="utf-8")
    assert "IE00BK5BQT80" in investments
    assert "IE00BG47KH54" in investments
    assert "IE00B4ND3602" in investments


def test_run_rebalance_execute_is_idempotent_after_execution(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    run_rebalance(
        MOVEMENTS_FILE,
        investments_file,
        sales_file,
        price_provider=_price_provider(),
        execute=True,
    )
    capsys.readouterr()

    run_rebalance(
        MOVEMENTS_FILE,
        investments_file,
        sales_file,
        price_provider=_price_provider(),
    )

    output = capsys.readouterr().out
    assert "Portfolio ya rebalanceado." in output


def test_run_rebalance_execute_rejects_changed_portfolio(tmp_path):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    class ChangingPriceProvider:
        def __init__(self):
            self.calls = 0

        def get_prices(self, symbols):
            self.calls += 1
            prices = _price_provider().get_prices(symbols)
            if self.calls > 1:
                prices["IE00BK5BQT80"] += Decimal("1")
            return prices

    try:
        run_rebalance(
            MOVEMENTS_FILE,
            investments_file,
            sales_file,
            price_provider=ChangingPriceProvider(),
            execute=True,
        )
    except ValueError as error:
        assert str(error) == "Portfolio changed since rebalance calculation"
    else:
        raise AssertionError("Expected ValueError")

    assert not investments_file.exists()
    assert not sales_file.exists()
