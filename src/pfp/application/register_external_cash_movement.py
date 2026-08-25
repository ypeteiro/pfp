from datetime import datetime
from decimal import Decimal

from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.infrastructure.external_cash_movement_repository import (
    ExternalCashMovementRepository,
)


def register_external_cash_movement(
    repository: ExternalCashMovementRepository,
    *,
    account_id: str,
    amount: Decimal,
    datetime: datetime,
    currency: str = "EUR",
    description: str | None = None,
) -> ExternalCashMovement:
    movement = ExternalCashMovement(
        datetime=datetime,
        account_id=account_id,
        amount=amount,
        currency=currency,
        description=description,
    )
    repository.save(movement)
    return movement
