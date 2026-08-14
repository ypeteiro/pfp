from decimal import Decimal
from pathlib import Path

from pfp.cli import load_portfolio, run_rebalance


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
    run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=_price_provider())
    output = capsys.readouterr().out
    assert "========== REBALANCEO ==========" in output
    assert "## ASIGNACIÓN" in output
    assert "## ÓRDENES" in output
    assert "Comandos ejecutables:" in output
    assert "Patrimonio total" in output
    assert "Patrimonio rebalanceable" in output
    assert "No rebalanceable" in output


def test_run_rebalance_execute_persists_orders(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"
    run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=_price_provider(), execute=True)
    output = capsys.readouterr().out
    assert "Rebalanceo ejecutado y persistido." in output
    investments = investments_file.read_text(encoding="utf-8")
    assert "IE00BK5BQT80" in investments
    buy_symbols = {line.split()[1] for line in output.splitlines() if line.startswith("BUY ")}
    for symbol in buy_symbols:
        assert symbol in investments


def test_run_rebalance_execute_is_idempotent_after_execution(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"
    run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=_price_provider(), execute=True)
    capsys.readouterr()
    run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=_price_provider())
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
        run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=ChangingPriceProvider(), execute=True)
    except ValueError as error:
        assert str(error) == "Portfolio changed since rebalance calculation"
    else:
        raise AssertionError("Expected ValueError")
    assert not investments_file.exists()
    assert not sales_file.exists()


def test_rebalance_execution_round_trip_reloads_consistent_portfolio(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"
    provider = _price_provider()
    before = load_portfolio(MOVEMENTS_FILE, investments_file, sales_file)
    initial_cash = before.cash
    run_rebalance(MOVEMENTS_FILE, investments_file, sales_file, price_provider=provider, execute=True)
    execute_output = capsys.readouterr().out
    after = load_portfolio(MOVEMENTS_FILE, investments_file, sales_file)
    assert investments_file.exists()
    assert after.cash < initial_cash
    assert after.invested > before.invested
    persisted_symbols = {
        row.split(",")[1]
        for row in investments_file.read_text(encoding="utf-8").splitlines()[1:]
    }
    assert persisted_symbols
    assert persisted_symbols.issubset(after.positions)
    sales = sales_file.read_text(encoding="utf-8") if sales_file.exists() else ""
    assert sales_file.exists() is ("SELL" in execute_output)
    if sales:
        assert "IE00" in sales
