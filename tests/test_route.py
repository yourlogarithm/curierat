import unittest

from classes.route import Route


class TestRoute(unittest.TestCase):
    def test_city_coordinates(self):
        lat, long = (21.13546 + 21.298038) / 2, (45.683601 + 45.806252) / 2  # coordinates from webpage api
        result_lat, result_long = Route._get_coordinates_of_city('Timisoara')
        self.assertAlmostEqual(lat, result_lat, delta=0.0001)
        self.assertAlmostEqual(long, result_long, delta=0.0001)

    def test_distance_and_duration(self):
        distance, duration = Route.get_distance_and_duration_between_cities('Timisoara', 'Craiova')
        self.assertAlmostEqual(distance, 340, delta=10)
        self.assertAlmostEqual(duration, 5, delta=1)
