"""Validation rules applied at import boundaries."""

from dataclasses import dataclass
from decimal import Decimal

from pfp.domain.movement import Movement


@dataclass(frozen=True, slots=True)
class ImportValidationIssue:
    row: int
    code: str
    message: str
    transaction_id: str | None = None


class ImportValidationError(ValueError):
    """Raised when imported data cannot safely enter the domain."""

    def __init__(self, issues: tuple[ImportValidationIssue, ...]):
        self.issues = issues
        details = "; ".join(f"fila {i.row}: {i.message}" for i in issues)
        super().__init__(f"Datos de importación inválidos ({len(issues)}): {details}")


def validate_movements(movements: list[Movement]) -> tuple[ImportValidationIssue, ...]:
    issues: list[ImportValidationIssue] = []
    seen_ids: dict[str, int] = {}

    for row, movement in enumerate(movements, start=2):
        tx = movement.transaction_id.strip() if movement.transaction_id else ""
        if not tx:
            issues.append(ImportValidationIssue(row, "MISSING_TRANSACTION_ID", "Falta el identificador de transacción."))
        elif tx in seen_ids:
            issues.append(ImportValidationIssue(row, "DUPLICATE_TRANSACTION_ID", f"Identificador duplicado (fila {seen_ids[tx]}).", tx))
        else:
            seen_ids[tx] = row

        if movement.datetime is None:
            issues.append(ImportValidationIssue(row, "MISSING_DATETIME", "Falta la fecha/hora.", tx or None))
        if not (movement.broker or "").strip():
            issues.append(ImportValidationIssue(row, "MISSING_BROKER", "Falta el broker.", tx or None))
        if not (movement.category or "").strip():
            issues.append(ImportValidationIssue(row, "MISSING_CATEGORY", "Falta la categoría.", tx or None))
        if not (movement.type or "").strip():
            issues.append(ImportValidationIssue(row, "MISSING_TYPE", "Falta el tipo de movimiento.", tx or None))
        if not (movement.currency or "").strip() or len(movement.currency.strip()) != 3:
            issues.append(ImportValidationIssue(row, "INVALID_CURRENCY", f"Divisa inválida: {movement.currency!r}.", tx or None))

        for field, value in (("amount", movement.amount), ("fee", movement.fee), ("tax", movement.tax)):
            if not isinstance(value, Decimal) or not value.is_finite():
                issues.append(ImportValidationIssue(row, "NON_FINITE_AMOUNT", f"{field} no es un importe decimal finito.", tx or None))
        if movement.shares is not None and movement.shares < Decimal("0"):
            issues.append(ImportValidationIssue(row, "NEGATIVE_SHARES", "Las participaciones no pueden ser negativas.", tx or None))
        if movement.price is not None and movement.price < Decimal("0"):
            issues.append(ImportValidationIssue(row, "NEGATIVE_PRICE", "El precio no puede ser negativo.", tx or None))

    return tuple(issues)
