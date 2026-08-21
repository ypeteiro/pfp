from pathlib import Path
from decimal import Decimal

from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("tests/fixtures/trade_republic.csv")


def test_trade_republic_fixture_has_25000_eur_of_external_contributions():
    importer = TradeRepublicImporter()

    flows = importer.load_capital_flows(CSV_FILE)

    contributions = [flow for flow in flows if flow.flow_type.value == "CONTRIBUTION"]
    withdrawals = [flow for flow in flows if flow.flow_type.value == "WITHDRAWAL"]

    assert len(contributions) == 7
    assert sum((flow.amount for flow in contributions), Decimal("0")) == Decimal("25000")
    assert withdrawals == []
    assert len({flow.transaction_id for flow in contributions}) == len(contributions)
