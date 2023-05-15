from datetime import datetime, timedelta

from classes.open_route_service import OpenRouteService
from classes.raw_route import RawRoute
from constants import TEST_DEFAULT_PASSWORD
from tests.test_client import TestClient


class TestRoute(TestClient):
    def test_city_coordinates(self):
        lat, long = (21.13546 + 21.298038) / 2, (45.683601 + 45.806252) / 2  # coordinates from webpage api
        result_lat, result_long = OpenRouteService._get_coordinates_of_city('Timisoara')
        self.assertAlmostEqual(lat, result_lat, delta=0.01)
        self.assertAlmostEqual(long, result_long, delta=0.01)

    def test_distance_and_duration(self):
        data = OpenRouteService.get_route_data(['Timisoara', 'Craiova', 'Bucuresti'])
        self.assertAlmostEqual(data['total_distance'], 580, delta=20)
        self.assertAlmostEqual(data['total_duration'], 31000, delta=3600)

    def test_add_route(self):
        raw_route = RawRoute(cities=['Timisoara', 'Arad', 'Oradea'], start=datetime.now() + timedelta(days=5), transport='TRUCK4')
        response = self.client.post('/routes/add', json=raw_route.to_dict(), headers=self.authorize('admin',  TEST_DEFAULT_PASSWORD))
        self.assertEqual(response.status_code, 200)
