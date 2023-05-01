from datetime import datetime, timedelta

from fastapi.testclient import TestClient as FastApiTestClient
from unittest import TestCase
from classes.database import CollectionProvider
from classes.route import Route, RawRoute
from constants import TEST_DEFAULT_HASHED_PASSWORD
from main import app


class TestClient(TestCase):
    client = FastApiTestClient(app)

    @staticmethod
    def clear_db():
        CollectionProvider.users().drop()
        CollectionProvider.users().insert_many([
            {"username": "admin", "email": "admin@curierat.com", "fullname": "Admin", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 4, "disabled": False},
            {"username": "moderator", "email": "moderator@curierat.com", "fullname": "Moderator", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 3, "disabled": False},
            {"username": "office", "email": "office@curierat.com", "fullname": "Office", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 2, "disabled": False},
            {"username": "courier", "email": "courier@curierat.com", "fullname": "Courier", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 1, "disabled": False},
            {"username": "client", "email": "client@curierat.com", "fullname": "Client", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 0, "disabled": False}
        ])

    @classmethod
    def setUpClass(cls):
        cls.clear_db()
        CollectionProvider.routes().drop()
        CollectionProvider.transports().drop()
        CollectionProvider.transports().insert_many([
            {"id": "TRUCK1", "cargo_category": 0},
            {"id": "TRUCK2", "cargo_category": 1},
            {"id": "TRUCK3", "cargo_category": 2},
        ])
        CollectionProvider.routes().insert_many([
            Route.from_raw_route(RawRoute(**{
                "cities": ["Timisoara", "Craiova", "Bucuresti"],
                "start": datetime.now() + timedelta(days=1),
                "transport": "TRUCK1"})).to_dict(),
            Route.from_raw_route(RawRoute(**{
                "cities": ["Bucuresti", "Craiova", "Timisoara"],
                "start": datetime.now() + timedelta(days=6),
                "transport": "TRUCK1"})).to_dict(),
            Route.from_raw_route(RawRoute(**{
                "cities": ["Iasi", "Brasov", "Cluj"],
                "start": datetime.now() + timedelta(days=2),
                "transport": "TRUCK2"})).to_dict(),
            Route.from_raw_route(RawRoute(**{
                "cities": ["Bucuresti", "Constanta", "Galati"],
                "start": datetime.now() + timedelta(days=3),
                "transport": "TRUCK3"})).to_dict(),
        ])

    @classmethod
    def authorize(cls, username: str, password: str):
        access_token = cls.client.post("/token", data={"username": username, "password": password}).json()['access_token']
        return {"Authorization": f"Bearer {access_token}"}

    def test_db(self):
        self.assertEqual(CollectionProvider.get_database_name(), "test_curierat")
