from classes.database import CollectionProvider
from constants import TEST_DEFAULT_PASSWORD, TEST_DEFAULT_HASHED_PASSWORD
from tests.test_client import TestClient


class UsersTest(TestClient):
    TEST_USER_REGISTER_FORM = {
            "username": "test",
            "email": "test@curierat.ro",
            "fullname": "Test",
            "password": "password",
            "access_level": 0,
    }

    @classmethod
    def setUp(cls):
        CollectionProvider.users().drop()
        CollectionProvider.users().insert_many([
            {"username": "admin", "email": "admin@curierat.com", "fullname": "Admin", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 4, "disabled": False},
            {"username": "moderator", "email": "moderator@curierat.com", "fullname": "Moderator", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 3, "disabled": False},
            {"username": "office", "email": "office@curierat.com", "fullname": "Office", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 2, "disabled": False},
            {"username": "courier", "email": "courier@curierat.com", "fullname": "Courier", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 1, "disabled": False},
            {"username": "client", "email": "client@curierat.com", "fullname": "Client", "hashed_password": TEST_DEFAULT_HASHED_PASSWORD, "access_level": 0, "disabled": False}
        ])

    def test_add_user_as_non_privileged(self):
        response = self.client.post("/users/add", headers=self.authorize("client", TEST_DEFAULT_PASSWORD), json=self.TEST_USER_REGISTER_FORM)
        self.assertEqual(403, response.status_code)

    def test_add_user_as_privileged(self):
        response = self.client.post("/users/add", headers=self.authorize("moderator", TEST_DEFAULT_PASSWORD), json=self.TEST_USER_REGISTER_FORM)
        self.assertEqual(200, response.status_code)

    def test_add_moderator_as_non_privileged(self):
        user_to_add = self.TEST_USER_REGISTER_FORM.copy()
        user_to_add["access_level"] = 3
        response = self.client.post("/users/add", headers=self.authorize("moderator", TEST_DEFAULT_PASSWORD), json=user_to_add)
        self.assertEqual(403, response.status_code)
        user_to_add["access_level"] = 4
        response = self.client.post("/users/add", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=user_to_add)
        self.assertEqual(403, response.status_code)

    def test_add_admin_as_privileged(self):
        user_to_add = self.TEST_USER_REGISTER_FORM.copy()
        user_to_add["access_level"] = 4
        response = self.client.post("/users/add", headers=self.authorize("admin", TEST_DEFAULT_PASSWORD), json=user_to_add)
        self.assertEqual(200, response.status_code)

    def test_delete_user_as_non_privileged(self):
        response = self.client.get("/users/delete/test", headers=self.authorize("moderator", TEST_DEFAULT_PASSWORD))
        self.assertEqual(403, response.status_code)

    def test_delete_user_as_privileged(self):
        self.client.post("/users/add", headers=self.authorize("moderator", TEST_DEFAULT_PASSWORD), json=self.TEST_USER_REGISTER_FORM)
        response = self.client.get("/users/delete/test", headers=self.authorize("admin", TEST_DEFAULT_PASSWORD))
        self.assertEqual(200, response.status_code)
