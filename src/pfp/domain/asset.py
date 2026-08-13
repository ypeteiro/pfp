from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Asset:
    symbol: str
    name: str
    portfolio_class: str
    isin: str | None = None
    ticker: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Asset symbol must not be empty")
        if not self.name.strip():
            raise ValueError("Asset name must not be empty")
        if not self.portfolio_class.strip():
            raise ValueError("Asset portfolio_class must not be empty")
