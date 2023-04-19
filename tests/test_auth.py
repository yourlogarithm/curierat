from unittest import TestCase
from fastapi.testclient import TestClient
from classes.database import CollectionProvider
from constants import TEST_DEFAULT_PASSWORD, TEST_DEFAULT_HASHED_PASSWORD
from main import app

client = TestClient(app)


class AuthTest(TestCase):

    @classmethod
    def setUpClass(cls):
        CollectionProvider.users().drop()
        CollectionProvider.users().insert_many([
            {"username": "admin", "email": "admin@curierat.com", "fullname": "Admin", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 3, "disabled": False},
            {"username": "office", "email": "office@curierat.com", "fullname": "Office", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 2, "disabled": False},
            {"username": "courier", "email": "courier@curierat.com", "fullname": "Courier", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 1, "disabled": False},
            {"username": "client", "email": "client@curierat.com", "fullname": "Client", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 0, "disabled": False}
        ])

    def test_register_client_with_higher_access_level(self):
        response = client.post("/users/register_client", json={
            "username": "higher_access_level_test",
            "email": "higher_access_level_test@gmail.com",
            "fullname": "Higher Access Level Test",
            "disabled": False,
            "password": "password",
            "access_level": 3,
            "test": True
        })
        self.assertEqual(403, response.status_code)

    def test_register_client_with_proper_access_level(self):
        response = client.post("/users/register_client", json={
            "username": "proper_access_level_test",
            "email": "proper_access_level_test@gmail.com",
            "fullname": "Proper Access Level Test",
            "disabled": False,
            "password": "password",
            "access_level": 0,
            "test": True
        })
        self.assertEqual(200, response.status_code)

    def test_register_employee_as_client(self):
        access_token = client.post("/token", data={"username": "client", "password": TEST_DEFAULT_PASSWORD}).json()['access_token']
        response = client.post(
            "/users/register_employee",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"username": "client_access_level_test", "email": "client_access_level_test@gmail.com", "fullname": "Client Access Level Test", "disabled": False, "password": "password",
                  "access_level": 3}
        )
        self.assertEqual(403, response.status_code)

    def test_register_employee_as_admin(self):
        access_token = client.post("/token", data={"username": "admin", "password": TEST_DEFAULT_PASSWORD}).json()['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"username": "client_access_level_test", "email": "client_access_level_test@gmail.com", "fullname": "Client Access Level Test", "disabled": False, "password": "password",
                "access_level": 0}
        response = client.post("/users/register_employee", headers=headers, json=data)
        assert response.status_code == 403

        data["access_level"] = 3
        response = client.post("/users/register_employee", headers=headers, json=data)
        self.assertEqual(200, response.status_code)
