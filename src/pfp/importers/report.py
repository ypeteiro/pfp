"""Structured result for portfolio imports."""

from dataclasses import dataclass

from pfp.domain.movement import Movement
from pfp.importers.validation import ImportValidationIssue


@dataclass(frozen=True, slots=True)
class ImportReport:
    """Summary of an import before the caller decides whether to accept it."""

    movements: tuple[Movement, ...]
    issues: tuple[ImportValidationIssue, ...]

    @property
    def processed(self) -> int:
        return len(self.movements)

    @property
    def error_count(self) -> int:
        return len(self.issues)

    @property
    def ok(self) -> bool:
        return not self.issues
