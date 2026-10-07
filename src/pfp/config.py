from decimal import Decimal, InvalidOperation
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


def save_target_allocation(allocation, path=DEFAULT_CONFIG_FILE):
    config_path = Path(path)
    normalized = {}
    for portfolio_class, value in allocation.items():
        key = str(portfolio_class).strip().lower()
        try:
            percentage = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Objetivo no válido para {portfolio_class}") from exc
        if percentage < 0 or percentage > 100:
            raise ValueError(f"El objetivo de {portfolio_class} debe estar entre 0 y 100")
        normalized[key] = percentage

    if not normalized:
        raise ValueError("Portfolio target allocation cannot be empty")
    total = sum(normalized.values(), Decimal("0"))
    if total != Decimal("100"):
        raise ValueError(f"Los objetivos deben sumar 100%, no {total}%")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for portfolio_class, percentage in normalized.items():
        lines.extend((f"[{portfolio_class}]", f"target = {percentage / Decimal('100')}", ""))
    config_path.write_text("\n".join(lines), encoding="utf-8")
