from decimal import Decimal


def normalize_price(
    price: Decimal,
    currency: str,
) -> Decimal:

    if currency == "GBp":
        return price / Decimal("100")

    if currency in {"EUR", "GBP", "USD"}:
        return price

    raise ValueError(
        f"Unsupported market currency: {currency}"
    )