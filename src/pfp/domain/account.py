from dataclasses import dataclass
from decimal import Decimal
@dataclass(slots=True)
class Account:
    name:str
    broker:str
    balance:Decimal=Decimal('0')
