from fastapi.testclient import TestClient as FastApiTestClient
from unittest import TestCase
from classes.database import CollectionProvider
from main import app


class TestClient(TestCase):
    client = FastApiTestClient(app)

    @classmethod
    def authorize(cls, username: str, password: str):
        access_token = cls.client.post("/token", data={"username": username, "password": password}).json()['access_token']
        return {"Authorization": f"Bearer {access_token}"}

    def test_db(self):
        self.assertEqual(CollectionProvider.get_database_name(), "test_curierat")
