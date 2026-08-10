from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.investment import Investment
from pfp.importers.investment_repository import (
    InvestmentRepository,
)


def test_save_and_load_investment(tmp_path):

    path = tmp_path / "investments.csv"

    repository = InvestmentRepository(
        path
    )

    investment = Investment(
        datetime=datetime(
            2026,
            8,
            10,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        symbol="IE00BG47KH54",
        shares=Decimal("2.5"),
        amount=Decimal("300"),
        price=Decimal("120"),
        portfolio_class="FIXED_INCOME",
        broker="Trade Republic",
    )

    repository.save(
        investment
    )

    investments = repository.load()

    assert len(investments) == 1

    loaded = investments[0]

    assert loaded.datetime == investment.datetime
    assert loaded.symbol == "IE00BG47KH54"
    assert loaded.shares == Decimal("2.5")
    assert loaded.amount == Decimal("300")
    assert loaded.price == Decimal("120")
    assert loaded.portfolio_class == "FIXED_INCOME"
    assert loaded.broker == "Trade Republic"


def test_save_creates_parent_directory(
    tmp_path,
):

    path = (
        tmp_path
        / "data"
        / "imports"
        / "investments.csv"
    )

    repository = InvestmentRepository(
        path
    )

    investment = Investment(
        datetime=datetime.now(
            timezone.utc
        ),
        symbol="TEST",
        shares=Decimal("1"),
        amount=Decimal("100"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        broker="Trade Republic",
    )

    repository.save(
        investment
    )

    assert path.exists()


def test_load_missing_file_returns_empty_list(
    tmp_path,
):

    path = tmp_path / "missing.csv"

    repository = InvestmentRepository(
        path
    )

    assert repository.load() == []


def test_save_multiple_investments(
    tmp_path,
):

    path = tmp_path / "investments.csv"

    repository = InvestmentRepository(
        path
    )

    first = Investment(
        datetime=datetime(
            2026,
            8,
            10,
            tzinfo=timezone.utc,
        ),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        broker="Trade Republic",
    )

    second = Investment(
        datetime=datetime(
            2026,
            8,
            11,
            tzinfo=timezone.utc,
        ),
        symbol="TEST",
        shares=Decimal("3"),
        amount=Decimal("360"),
        price=Decimal("120"),
        portfolio_class="EQUITY",
        broker="Trade Republic",
    )

    repository.save(first)
    repository.save(second)

    investments = repository.load()

    assert len(investments) == 2

    assert investments[0].shares == Decimal("2")
    assert investments[0].amount == Decimal("200")

    assert investments[1].shares == Decimal("3")
    assert investments[1].amount == Decimal("360")
