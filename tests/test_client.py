from fastapi.testclient import TestClient as FastApiTestClient
from unittest import TestCase
from classes.database import CollectionProvider
from constants import TEST_DEFAULT_HASHED_PASSWORD
from main import app


class TestClient(TestCase):
    client = FastApiTestClient(app)

    @staticmethod
    def clear_db():
        CollectionProvider.users().drop()
        CollectionProvider.users().insert_many([
            {"username": "admin", "email": "admin@curierat.com", "fullname": "Admin", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 0, "disabled": False},
            {"username": "moderator", "email": "moderator@curierat.com", "fullname": "Moderator", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 1, "disabled": False},
            {"username": "office", "email": "office@curierat.com", "fullname": "Office", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 2, "disabled": False},
            {"username": "courier", "email": "courier@curierat.com", "fullname": "Courier", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 3, "disabled": False},
            {"username": "client", "email": "client@curierat.com", "fullname": "Client", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 4, "disabled": False}
        ])

    @classmethod
    def setUpClass(cls):
        cls.clear_db()

    @classmethod
    def authorize(cls, username: str, password: str):
        access_token = cls.client.post("/token", data={"username": username, "password": password}).json()['access_token']
        return {"Authorization": f"Bearer {access_token}"}

    def test_db(self):
        self.assertEqual(CollectionProvider.get_database_name(), "test_curierat")
