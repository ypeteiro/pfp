"""Validation of imported portfolio report data."""

from dataclasses import dataclass
from decimal import Decimal

from pfp.reporting.portfolio_report import MovementReport, PortfolioReport


@dataclass(frozen=True, slots=True)
class DataQualityIssue:
    code: str
    message: str
    transaction_id: str | None = None
    severity: str = "error"


def validate_report(report: PortfolioReport) -> tuple[DataQualityIssue, ...]:
    """Return deterministic validation issues without mutating the report."""
    issues: list[DataQualityIssue] = []
    seen_ids: set[str] = set()

    for movement in report.movements:
        issues.extend(_validate_movement(movement))
        if movement.transaction_id in seen_ids:
            issues.append(DataQualityIssue(
                "DUPLICATE_TRANSACTION_ID",
                f"Transaction ID duplicado: {movement.transaction_id}",
                movement.transaction_id,
            ))
        elif movement.transaction_id:
            seen_ids.add(movement.transaction_id)

    if report.market_value < Decimal("0"):
        issues.append(DataQualityIssue("NEGATIVE_MARKET_VALUE", "El valor de mercado no puede ser negativo."))
    if report.cash < Decimal("0"):
        issues.append(DataQualityIssue("NEGATIVE_CASH", "El efectivo no puede ser negativo."))

    for position in report.positions:
        if position.shares < Decimal("0"):
            issues.append(DataQualityIssue("NEGATIVE_SHARES", f"Participaciones negativas para {position.symbol}."))
        if position.invested < Decimal("0"):
            issues.append(DataQualityIssue("NEGATIVE_INVESTED", f"Capital invertido negativo para {position.symbol}."))
        if position.market_value is not None and position.market_value < Decimal("0"):
            issues.append(DataQualityIssue("NEGATIVE_POSITION_VALUE", f"Valor de mercado negativo para {position.symbol}."))

    return tuple(issues)


def _validate_movement(movement: MovementReport) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    tx = movement.transaction_id or None
    if movement.datetime is None:
        issues.append(DataQualityIssue("MISSING_DATETIME", "Movimiento sin fecha.", tx))
    if not movement.broker.strip():
        issues.append(DataQualityIssue("MISSING_BROKER", "Movimiento sin broker.", tx))
    if not movement.category.strip():
        issues.append(DataQualityIssue("MISSING_CATEGORY", "Movimiento sin categoría.", tx))
    if not movement.type.strip():
        issues.append(DataQualityIssue("MISSING_TYPE", "Movimiento sin tipo.", tx))
    if not movement.transaction_id.strip():
        issues.append(DataQualityIssue("MISSING_TRANSACTION_ID", "Movimiento sin identificador de transacción.", tx))
    if not movement.currency or len(movement.currency.strip()) != 3:
        issues.append(DataQualityIssue("INVALID_CURRENCY", f"Divisa inválida: {movement.currency!r}.", tx))
    if not movement.amount.is_finite():
        issues.append(DataQualityIssue("NON_FINITE_AMOUNT", "Importe no finito.", tx))
    if not movement.fee.is_finite() or not movement.tax.is_finite():
        issues.append(DataQualityIssue("NON_FINITE_CHARGES", "Comisión o impuesto no finito.", tx))
    if movement.shares is not None and movement.shares < Decimal("0"):
        issues.append(DataQualityIssue("NEGATIVE_MOVEMENT_SHARES", "Participaciones negativas en movimiento.", tx))
    return issues
