from decimal import Decimal

import pytest

from pfp.config import load_target_allocation


def test_load_target_allocation():
    allocation = load_target_allocation()

    assert allocation == {
        "EQUITY": Decimal("75.00"),
        "FIXED_INCOME": Decimal("20.00"),
        "GOLD": Decimal("5.00"),
    }


def test_load_target_allocation_accepts_custom_toml(tmp_path):
    path = tmp_path / "portfolio.toml"
    path.write_text(
        "[equity]\ntarget = 0.60\n\n"
        "[fixed_income]\ntarget = 0.30\n\n"
        "[gold]\ntarget = 0.10\n",
        encoding="utf-8",
    )

    allocation = load_target_allocation(path)

    assert allocation == {
        "EQUITY": Decimal("60.00"),
        "FIXED_INCOME": Decimal("30.00"),
        "GOLD": Decimal("10.00"),
    }


def test_load_target_allocation_requires_100_percent(tmp_path):
    path = tmp_path / "portfolio.toml"
    path.write_text(
        "[equity]\ntarget = 0.70\n\n"
        "[fixed_income]\ntarget = 0.20\n\n"
        "[gold]\ntarget = 0.20\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must sum to 1.0"):
        load_target_allocation(path)


def test_load_target_allocation_rejects_negative_target(tmp_path):
    path = tmp_path / "portfolio.toml"
    path.write_text(
        "[equity]\ntarget = 1.10\n\n"
        "[fixed_income]\ntarget = -0.10\n\n"
        "[gold]\ntarget = 0.00\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cannot contain negative"):
        load_target_allocation(path)
