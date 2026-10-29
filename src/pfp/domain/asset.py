from dataclasses import dataclass


LONG_TERM = "LONG_TERM"
TACTICAL = "TACTICAL"


@dataclass(frozen=True, slots=True)
class Asset:
    symbol: str
    name: str
    portfolio_class: str
    isin: str | None = None
    ticker: str | None = None
    investment_strategy: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Asset symbol must not be empty")
        if not self.name.strip():
            raise ValueError("Asset name must not be empty")
        if not self.portfolio_class.strip():
            raise ValueError("Asset portfolio_class must not be empty")
        strategy = self.investment_strategy
        if strategy is None:
            strategy = TACTICAL if self.portfolio_class.strip().upper() == "STOCK" else LONG_TERM
            object.__setattr__(self, "investment_strategy", strategy)
        if strategy not in {LONG_TERM, TACTICAL}:
            raise ValueError("Asset investment_strategy must be LONG_TERM or TACTICAL")
