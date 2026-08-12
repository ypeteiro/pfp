from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.investment import Investment
from pfp.importers.investment_repository import InvestmentRepository


def test_save_and_load_investment(tmp_path):
    path = tmp_path / "investments.csv"
    repository = InvestmentRepository(path)

    investment = Investment(
        datetime=datetime(2026, 8, 10, 12, 30, tzinfo=timezone.utc),
        symbol="IE00BG47KH54",
        shares=Decimal("2.5"),
        amount=Decimal("300"),
        price=Decimal("120"),
        portfolio_class="FIXED_INCOME",
        broker="Trade Republic",
        operation_id="op-1",
    )

    repository.save(investment)
    loaded = repository.load()[0]

    assert loaded == investment


def test_save_creates_parent_directory(tmp_path):
    path = tmp_path / "data" / "imports" / "investments.csv"
    repository = InvestmentRepository(path)

    repository.save(
        Investment(
            datetime=datetime.now(timezone.utc),
            symbol="TEST",
            shares=Decimal("1"),
            amount=Decimal("100"),
            price=Decimal("100"),
            portfolio_class="EQUITY",
            broker="Trade Republic",
        )
    )

    assert path.exists()


def test_load_missing_file_returns_empty_list(tmp_path):
    assert InvestmentRepository(tmp_path / "missing.csv").load() == []


def test_save_multiple_investments(tmp_path):
    repository = InvestmentRepository(tmp_path / "investments.csv")

    first = Investment(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        broker="Trade Republic",
    )
    second = Investment(
        datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
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
    assert investments[1].shares == Decimal("3")


def test_save_with_same_operation_id_is_idempotent(tmp_path):
    repository = InvestmentRepository(tmp_path / "investments.csv")
    first = Investment(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        operation_id="rebalance-1",
    )
    duplicate = Investment(
        datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
        operation_id="rebalance-1",
    )

    repository.save(first)
    repository.save(duplicate)

    investments = repository.load()
    assert len(investments) == 1
    assert investments[0] == first
