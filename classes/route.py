from dataclasses import dataclass

import requests
from datetime import datetime, timedelta
from typing import List, Tuple

from pydantic import BaseModel
from constants import ORS_COORDS_URL, ORS_DISTANCE_URL, ORS_HEADERS


class RawRoute(BaseModel):
    cities: List[str]
    start: datetime
    transport: str


@dataclass
class Route:
    cities: List[str]
    transport: str
    coordinates: List[Tuple[float, float]]
    schedule: List[datetime]
    current_position: int

    @staticmethod
    def get_coordinates_of_city(city: str) -> Tuple[float, float]:
        data = requests.get(ORS_COORDS_URL + city).json()
        return tuple(data['features'][0]['geometry']['coordinates'])

    @staticmethod
    def get_coordinates_of_cities(cities: List[str]):
        return [Route.get_coordinates_of_city(city) for city in cities]

    @staticmethod
    def get_distance_and_duration_between_coords(coordinates: List[Tuple[float, float]]) -> Tuple[List[float], List[float]]:
        """
        :param coordinates: list of tuples of coordinates [(lat, lon), (lat, lon), ...]
        :return: Two lists, one with distances (km) and one with durations (seconds)
        """
        data = requests.post(ORS_DISTANCE_URL, headers=ORS_HEADERS, json={"coordinates": coordinates, "units": "km"}).json()
        distances, durations = [], []
        for segment in data["routes"][0]["segments"]:
            distances.append(segment["distance"])
            durations.append(segment["duration"])

        return distances, durations

    @classmethod
    def from_raw_route(cls, raw_route: RawRoute):
        coordinates = Route.get_coordinates_of_cities(raw_route.cities)
        distances, durations = Route.get_distance_and_duration_between_coords(coordinates)
        schedule = [raw_route.start]
        for duration in durations:
            schedule.append(schedule[-1] + timedelta(seconds=duration))
        return cls(cities=raw_route.cities, transport=raw_route.transport, coordinates=coordinates, schedule=schedule, current_position=0)

    def to_dict(self):
        return {
            "cities": self.cities,
            "transport": self.transport,
            "current_position": self.current_position,
            "schedule": self.schedule,
            "coordinates": self.coordinates
        }
