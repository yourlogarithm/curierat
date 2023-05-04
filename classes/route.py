from dataclasses import dataclass

from datetime import datetime, timedelta
from typing import List, Dict, Mapping

from bson import ObjectId

from classes.database import DatabaseProvider
from classes.open_route_service import OpenRouteService
from classes.raw_route import RawRoute
from classes.package import Package
from classes.transport import Transport


@dataclass
class Route:
    cities: List[str]
    transport: Transport
    schedule: List[datetime]
    current_position: int
    packages: List[Package]
    current_weight: float
    id: ObjectId = None

    @staticmethod
    def get_best_routes(origin: str, destination: str, timestamp: datetime) -> List['Route']:
        documents = list(DatabaseProvider.routes().aggregate([
            {
                "$match": {
                    "cities": {"$all": [origin, destination]},
                    "schedule": {"$gt": timestamp}
                },
            },
            {
                "$project": {
                    "office_index": {"$indexOfArray": ["$cities", origin]},
                    "destination_index": {"$indexOfArray": ["$cities", destination]},
                    "transport": 1,
                    "coordinates": 1,
                    "schedule": 1,
                    "current_position": 1,
                    "packages": 1,
                    "current_weight": 1,
                    "cities": 1,
                }
            },
            {"$match": {"$expr": {"$lt": ["$office_index", "$destination_index"]}}},
            {"$match": {"$expr": {"$lte": ["$office_index", "$current_position"]}}},
            {"$sort": {"schedule": 1}}
        ]))
        return [Route.from_dict(document) for document in documents]

    @classmethod
    def from_raw_route(cls, raw_route: RawRoute):
        data = OpenRouteService.get_route_data(raw_route.cities)
        schedule = [raw_route.start]
        for duration in data['durations']:
            schedule.append(schedule[-1] + timedelta(seconds=duration))
        transport = DatabaseProvider.transports().find_one({"_id": raw_route.transport})
        if transport is None:
            raise ValueError("Transport not found")
        return cls(cities=raw_route.cities, transport=transport, schedule=schedule, current_position=0, packages=[], current_weight=0)

    @classmethod
    def from_dict(cls, data: Dict | Mapping):
        return cls(
            id=data["_id"],
            cities=data["cities"],
            transport=Transport.from_dict(data["transport"]),
            schedule=data["schedule"],
            current_position=data["current_position"],
            packages=[Package.from_dict(package) for package in data["packages"]],
            current_weight=data["current_weight"]
        )

    def add_package(self, package: Package):
        self.packages.append(package)
        self.current_weight += package.weight
        DatabaseProvider.routes().update_one({"_id": self.id}, {"$push": {"packages": package.to_dict()}, "$set": {"current_weight": self.current_weight}})

    def to_dict(self):
        dict_val = {
            "cities": self.cities,
            "transport": self.transport,
            "current_position": self.current_position,
            "schedule": self.schedule,
            "packages": [package.to_dict() for package in self.packages],
            "current_weight": self.current_weight,
        }
        if self.id:
            dict_val["_id"] = self.id
        return dict_val
