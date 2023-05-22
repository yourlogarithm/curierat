from typing import List

import requests

from classes.coordinates import Coordinates
from classes.database_provider import DatabaseProvider
from constants import ORS_COORDS_URL, ORS_DISTANCE_URL, ORS_HEADERS


class OpenRouteService:
    @staticmethod
    def _get_coordinates_of_city(city: str) -> Coordinates:
        """
        :param city: city name
        :return: (lat, lon)
        """
        if (entry := DatabaseProvider.cities().find_one({'name': city})) is not None:
            return Coordinates(*entry['coordinates'])
        data = requests.get(ORS_COORDS_URL + city).json()
        coordinates = data['features'][0]['geometry']['coordinates']
        DatabaseProvider.cities().insert_one({'name': city, 'coordinates': coordinates, 'relations': {}})
        return Coordinates(*coordinates)

    @classmethod
    def _get_coordinates_of_cities(cls, cities: List[str]):
        """
        :param cities:
        :return: List of Coordinates
        """
        return [cls._get_coordinates_of_city(city) for city in cities]

    @staticmethod
    def _query_route_data_from_db(cities: List[str], data: dict) -> dict | None:
        queried_cities = list(DatabaseProvider.cities().find({'name': {'$in': cities}}))
        if len(queried_cities) == len(cities):
            mapped_values = {}
            cities_set = set(cities)
            for document in queried_cities:
                city_name = document['name']
                mapped_values[city_name] = {}
                for related_city, value in document['relations'].items():
                    if related_city in cities_set:
                        mapped_values[city_name][related_city] = value
                        distance = value['distance']
                        duration = value['duration']
                        mapped_values[city_name][related_city] = {'distance': distance, 'duration': duration}
            for i in range(len(cities)):
                city = cities[i]
                if i + 1 < len(cities):
                    next_city = cities[i + 1]
                    if next_city not in mapped_values[city]:
                        return None
                    data['total_distance'] += mapped_values[city][next_city]['distance']
                    data['total_duration'] += mapped_values[city][next_city]['duration']
                    data['distances'].append(mapped_values[city][next_city]['distance'])
                    data['durations'].append(mapped_values[city][next_city]['duration'])
                else:
                    return data
        return None

    @classmethod
    def get_route_data(cls, cities: List[str]) -> dict:
        """
        :param cities: list of city names
        :return: Two lists, one with distances (km) and one with durations (seconds)
        """
        data = {
            'total_distance': 0,
            'total_duration': 0,
            'distances': [],
            'durations': []
        }
        db_data = cls._query_route_data_from_db(cities, data.copy())
        if db_data is not None:
            return db_data

        coordinates = cls._get_coordinates_of_cities(cities)
        result = requests.post(
            ORS_DISTANCE_URL,
            headers=ORS_HEADERS,
            json={'coordinates': [coordinate.to_tuple() for coordinate in coordinates], 'units': 'km'}
        ).json()['routes'][0]['segments']
        for i, segment in enumerate(result):
            distance, duration = segment['distance'], segment['duration']
            city, next_city = cities[i], cities[i+1]
            DatabaseProvider.cities().update_one(
                {'name': city},
                {'$set': {f'relations.{next_city}': {'distance': distance, 'duration': duration}}})
            DatabaseProvider.cities().update_one(
                {'name': next_city},
                {'$set': {'relations': {city: {'distance': distance, 'duration': duration}}}})
            data['total_distance'] += distance
            data['total_duration'] += duration
            data['distances'].append(distance)
            data['durations'].append(duration)
        return data
