from decimal import Decimal
from pathlib import Path

from pfp.cli import run_rebalance


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


def test_run_rebalance_prints_market_allocation_and_orders(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

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

    run_rebalance(
        MOVEMENTS_FILE,
        investments_file,
        sales_file,
        price_provider=StubPriceProvider(),
    )

    output = capsys.readouterr().out
    assert "========== REBALANCEO ==========" in output
    assert "## ASIGNACIÓN" in output
    assert "## ÓRDENES" in output
    assert "Comandos ejecutables:" in output
