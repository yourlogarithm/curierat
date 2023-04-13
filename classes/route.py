import requests
import json
from typing import List
from dotenv import get_key


class Route:
    API_KEY = get_key("../.env", "ORS_KEY")
    BASE_URL = "https://api.openrouteservice.org"
    COORDS_URL = f"{BASE_URL}/geocode/search/structured?api_key={API_KEY}&country=RO&boundary.country=RO&locality="
    DISTANCE_URL = f"{BASE_URL}/v2/directions/driving-car"
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf62485952f026751e4b9eaf2f62275d85a0fd"
    }

    @staticmethod
    def _get_coordinates_of_city(city: str):
        data = requests.get(Route.COORDS_URL + city).json()
        min_lat, min_lon, max_lat, max_lon = data["bbox"]
        return (min_lat + max_lat) / 2, (min_lon + max_lon) / 2

    @staticmethod
    def get_coordinates_of_cities(cities: List[str]):
        return [Route._get_coordinates_of_city(city) for city in cities]

    @staticmethod
    def get_distance_and_duration_between_cities(city1: str, city2: str):
        coords1 = list(Route._get_coordinates_of_city(city1))
        coords2 = list(Route._get_coordinates_of_city(city2))
        data = requests.post(Route.DISTANCE_URL, headers=Route.HEADERS, json={"coordinates": [coords1, coords2], "units": "km"}).json()
        result = data["routes"][0]["summary"]
        return result["distance"], result["duration"] / 3600

    def __init__(self, cities: List[str]):
        self.cities = cities
        self.coordinates = Route.get_coordinates_of_cities(cities)
