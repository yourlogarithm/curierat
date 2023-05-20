from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def to_tuple(self):
        return self.latitude, self.longitude
