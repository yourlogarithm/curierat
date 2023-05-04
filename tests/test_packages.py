from bson import ObjectId

from classes.database import DatabaseProvider
from classes.form import Form
from classes.package import Package
from constants import TEST_DEFAULT_PASSWORD
from tests.test_client import TestClient


class FormSubmissionTest(TestClient):
    TEST_FORM = {
        "sender_contact": {
            "first_name": "Sender First Name",
            "last_name": "Sender Last Name",
            "email": "sender@gmail.com",
            "phone": "0751234567"
        },
        "receiver_contact": {
            "first_name": "Receiver First Name",
            "last_name": "Receiver Last Name",
            "email": "sender@gmail.com",
            "phone": "0785123456"
        },
        "office": "Timisoara",
        "destination": "Bucuresti",
        "weight": 1.5,
        "category": 0
    }

    def get_package(self, origin: str = None, destination: str = None):
        dict_val = self.TEST_FORM.copy()
        if origin is not None and destination is not None:
            dict_val.update({"office": origin, "destination": destination})
        elif origin is not None:
            dict_val.update({"office": origin})
        elif destination is not None:
            dict_val.update({"destination": destination})
        dict_val.update({"price": Package.get_price(Form(**dict_val)), "closed": False})
        return dict_val

    def test_calculate_price(self):
        response = self.client.post("/packages/calculate_price", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=self.TEST_FORM)
        self.assertAlmostEqual(185.408925, float(response.text), delta=5)

    def test_add_package(self):
        package = self.get_package()
        id_ = self.client.post("/packages/add", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=package).text.replace('"', '')
        route = DatabaseProvider.routes().find_one({"_id": ObjectId(id_)})
        self.assertEqual(route["packages"][0]["sender_contact"]["first_name"], package["sender_contact"]["first_name"])

    def test_close_package(self):
        id0 = self.client.post("/packages/add", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=self.get_package('Iasi', 'Brasov')).text.replace('"', '')
        id1 = self.client.post("/packages/add", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=self.get_package('Iasi', 'Cluj')).text.replace('"', '')
        self.assertEqual(id0, id1)
        result = self.client.post(f"/packages/close_package/{id0}/Brasov", headers=self.authorize("courier", TEST_DEFAULT_PASSWORD))

