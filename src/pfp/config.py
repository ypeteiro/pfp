from decimal import Decimal
from pathlib import Path
import tomllib


DEFAULT_CONFIG_FILE = Path("config/portfolio.toml")


def load_target_allocation(path=DEFAULT_CONFIG_FILE):
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Portfolio configuration file not found: {config_path}"
        )

    with config_path.open("rb") as file:
        data = tomllib.load(file)

    target_allocation = {}
    for portfolio_class, values in data.items():
        if not isinstance(values, dict) or "target" not in values:
            raise ValueError(
                f"Invalid target allocation for {portfolio_class}"
            )
        target_allocation[portfolio_class.upper()] = (
            Decimal(str(values["target"])) * Decimal("100")
        )

    if not target_allocation:
        raise ValueError("Portfolio target allocation cannot be empty")

    total = sum(target_allocation.values())
    if total != Decimal("100"):
        raise ValueError(
            f"Portfolio target allocation must sum to 1.0, got {total / Decimal('100')}"
        )

    if any(value < 0 for value in target_allocation.values()):
        raise ValueError("Portfolio target allocation cannot contain negative values")

    return target_allocation
