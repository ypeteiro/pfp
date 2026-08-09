from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Asset:

    symbol: str
    name: str
    portfolio_class: str