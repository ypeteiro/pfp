from pathlib import Path
from decimal import Decimal

from pfp.cli import run_invest
from pfp.importers.investment_repository import (
    InvestmentRepository,
)


MOVEMENTS_FILE = Path(
    "data/imports/trade_republic.csv"
)


def test_run_invest_persists_investment(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    run_invest(
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    repository = InvestmentRepository(
        investments_file
    )

    investments = repository.load()

    assert len(investments) == 1

    investment = investments[0]

    assert investment.symbol == "TEST"
    assert investment.shares == Decimal("2")
    assert investment.amount == Decimal("200")
    assert investment.price == Decimal("100")
    assert investment.portfolio_class == "EQUITY"
    assert investment.broker == "Trade Republic"


def test_run_invest_uses_utc_datetime(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    run_invest(
        symbol="TEST",
        shares=Decimal("1"),
        amount=Decimal("100"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    repository = InvestmentRepository(
        investments_file
    )

    investments = repository.load()

    assert len(investments) == 1

    investment = investments[0]

    assert investment.datetime.tzinfo is not None
    assert (
        investment.datetime.utcoffset()
        is not None
    )
