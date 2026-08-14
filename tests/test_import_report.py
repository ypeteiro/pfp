from pathlib import Path

from pfp.importers.report import ImportReport
from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("data/imports/trade_republic.csv")


def test_trade_republic_import_report_is_structured():
    report = TradeRepublicImporter().load_report(CSV_FILE)

    assert isinstance(report, ImportReport)
    assert report.processed == 17
    assert report.error_count == 0
    assert report.ok is True
    assert len(report.movements) == 17


def test_load_keeps_strict_backward_compatible_contract():
    movements = TradeRepublicImporter().load(CSV_FILE)
    assert len(movements) == 17
