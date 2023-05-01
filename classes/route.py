from dataclasses import dataclass

from datetime import datetime, timedelta
from typing import List, Tuple

from pydantic import BaseModel

from classes.open_route_service import OpenRouteService
from classes.ticket import Ticket


class RawRoute(BaseModel):
    cities: List[str]
    start: datetime
    transport: str


@dataclass
class Route:
    cities: List[str]
    transport: str
    schedule: List[datetime]
    current_position: int
    tickets: List[Ticket]

    @classmethod
    def from_raw_route(cls, raw_route: RawRoute):
        data = OpenRouteService.get_route_data(raw_route.cities)
        schedule = [raw_route.start]
        for duration in data['durations']:
            schedule.append(schedule[-1] + timedelta(seconds=duration))
        return cls(cities=raw_route.cities, transport=raw_route.transport,
                   schedule=schedule, current_position=0, tickets=[])

    def to_dict(self):
        return {
            "cities": self.cities,
            "transport": self.transport,
            "current_position": self.current_position,
            "schedule": self.schedule
        }
