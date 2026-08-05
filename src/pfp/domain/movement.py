from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
@dataclass(slots=True)
class Movement:
    external_id:str
    date:datetime
    amount:Decimal
