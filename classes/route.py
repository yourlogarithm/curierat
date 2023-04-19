import requests
from datetime import datetime, timedelta
from typing import List, Tuple

from bson import ObjectId
from pydantic import BaseModel, PrivateAttr
from pymongo.collection import Collection
from constants import ORS_COORDS_URL, ORS_DISTANCE_URL, ORS_HEADERS


class Route(BaseModel):
    cities: List[str]
    start: datetime
    transport: str
    _coordinates: List[Tuple[float, float]] = PrivateAttr(None)
    _schedule: List[datetime] = PrivateAttr(None)
    _current_position: int = PrivateAttr(0)
    _id: ObjectId = PrivateAttr(None)

    @staticmethod
    def _get_coordinates_of_city(city: str) -> Tuple[float, float]:
        data = requests.get(ORS_COORDS_URL + city).json()
        return tuple(data['features'][0]['geometry']['coordinates'])

    @staticmethod
    def get_coordinates_of_cities(cities: List[str]):
        return [Route._get_coordinates_of_city(city) for city in cities]

    @staticmethod
    def get_distance_and_duration_between_coords(coordinates: List[Tuple[float, float]]) -> Tuple[List[float], List[float]]:
        """
        :param coordinates: list of tuples of coordinates
        :return: Two lists, one with distances (km) and one with durations (seconds)
        """
        data = requests.post(ORS_DISTANCE_URL, headers=ORS_HEADERS, json={"coordinates": coordinates, "units": "km"}).json()
        distances, durations = [], []
        for segment in data["routes"][0]["segments"]:
            distances.append(segment["distance"])
            durations.append(segment["duration"])

        return distances, durations

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._coordinates = Route.get_coordinates_of_cities(self.cities)
        self._id = kwargs.get("_id")
        distances, durations = Route.get_distance_and_duration_between_coords(self._coordinates)
        self._schedule = [self.start]
        for duration in durations:
            self._schedule.append(self._schedule[-1] + timedelta(seconds=duration))

    def dict(self, *args, **kwargs):
        return {
            "cities": self.cities,
            "transport": self.transport,
            "current_position": self._current_position,
            "schedule": self._schedule,
            "coordinates": self._coordinates
        }

    def update_current_position(self, collection: Collection, id_: str):
        self._current_position += 1
        collection.update_one({"_id": id_}, {"$set": {"current_position": self._current_position}})

    def change_transport(self, collection: Collection, id_: str, transport: str):
        self.transport = transport
        collection.update_one({"_id": id_}, {"$set": {"transport": transport}})
