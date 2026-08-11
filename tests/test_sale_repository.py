from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.sale import Sale
from pfp.importers.sale_repository import SaleRepository


def test_save_and_load_sale(tmp_path):
    path = tmp_path / "sales.csv"
    repository = SaleRepository(path)

    sale = Sale(
        datetime=datetime(2026, 8, 10, 12, 30, tzinfo=timezone.utc),
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        amount=Decimal("150"),
        price=Decimal("1500"),
    )

    repository.save(sale)

    loaded = repository.load()
    assert len(loaded) == 1
    assert loaded[0] == sale


def test_save_creates_parent_directory(tmp_path):
    path = tmp_path / "data" / "imports" / "sales.csv"
    repository = SaleRepository(path)

    repository.save(
        Sale(
            datetime=datetime.now(timezone.utc),
            symbol="TEST",
            shares=Decimal("1"),
            amount=Decimal("100"),
            price=Decimal("100"),
        )
    )

    assert path.exists()


def test_load_missing_file_returns_empty_list(tmp_path):
    assert SaleRepository(tmp_path / "missing.csv").load() == []
