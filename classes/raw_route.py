from datetime import datetime
from typing import List

from pydantic import BaseModel


class RawRoute(BaseModel):
    cities: List[str]
    start: datetime
    transport: str

    def to_dict(self):
        return {
            "cities": self.cities,
            "start": self.start.timestamp(),
            "transport": self.transport
        }
