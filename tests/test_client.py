from main import app
from fastapi.testclient import TestClient as FastApiTestClient
from unittest import TestCase


class TestClient(TestCase):
    client = FastApiTestClient(app)

    def authorize(self, username: str, password: str):
        access_token = self.client.post("/token", data={"username": username, "password": password}).json()['access_token']
        return {"Authorization": f"Bearer {access_token}"}
