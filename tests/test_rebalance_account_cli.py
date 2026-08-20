from decimal import Decimal

import pfp.cli as cli
from pfp.engine.rebalance_engine import Rebalance, RebalanceOrder


def _empty_rebalance():
    return Rebalance(
        total_value=Decimal("1000"),
        rebalanceable_value=Decimal("800"),
        allocations=(),
        orders=(),
    )


def test_rebalance_cli_defaults_to_trade_republic_account():
    args = cli.build_parser().parse_args(["rebalance", "movements.csv"])

    assert args.account_id == cli.DEFAULT_ACCOUNT_ID


def test_run_rebalance_passes_selected_account_to_calculation(monkeypatch, capsys):
    captured = {}

    def fake_build(movements_file, investments_file, sales_file, price_provider, account_id=cli.DEFAULT_ACCOUNT_ID):
        captured["account_id"] = account_id
        return _empty_rebalance()

    monkeypatch.setattr(cli, "_build_rebalance", fake_build)

    cli.run_rebalance("movements.csv", price_provider=object(), account_id="ABANCA_AHORRO")

    assert captured["account_id"] == "ABANCA_AHORRO"
    assert "Cuenta rebalanceada     : ABANCA_AHORRO" in capsys.readouterr().out


def test_run_rebalance_passes_selected_account_to_execution(monkeypatch):
    captured = {}
    order = RebalanceOrder(
        action="BUY",
        symbol="TEST",
        asset_name="Test ETF",
        portfolio_class="EQUITY",
        amount=Decimal("100"),
    )
    rebalance = Rebalance(
        total_value=Decimal("1000"),
        rebalanceable_value=Decimal("1000"),
        allocations=(),
        orders=(order,),
    )

    def fake_build(*args, **kwargs):
        return rebalance

    def fake_execute(*args, **kwargs):
        captured["account_id"] = kwargs["account_id"]

    monkeypatch.setattr(cli, "_build_rebalance", fake_build)
    monkeypatch.setattr(cli, "_execute_rebalance", fake_execute)

    cli.run_rebalance("movements.csv", price_provider=object(), execute=True, account_id="ABANCA_AHORRO")

    assert captured["account_id"] == "ABANCA_AHORRO"
