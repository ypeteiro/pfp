from pathlib import Path

from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("data/imports/trade_republic.csv")


def test_import_trade_republic():

    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    assert len(movements) == 17


def test_build_portfolio():

    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    assert len(portfolio.positions) == 9

    assert round(float(portfolio.cash), 2) == 3603.39

    assert round(float(portfolio.invested), 2) == 21396.61

    assert "BTC" in portfolio.positions

    assert "IE00BK5BQT80" in portfolio.positions

    assert "IE00BG47KH54" in portfolio.positions