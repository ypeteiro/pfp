from dataclasses import dataclass
@dataclass(slots=True)
class Asset:
    isin:str
    ticker:str
    name:str
