from bson import ObjectId

from classes.database import CollectionProvider
from constants import TEST_DEFAULT_PASSWORD, TEST_DEFAULT_HASHED_PASSWORD
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

    @classmethod
    def setUp(cls) -> None:
        CollectionProvider.tickets().drop()

    def test_calculate_price(self):
        response = self.client.post("/tickets/calculate_price", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=self.TEST_FORM)
        self.assertAlmostEqual(185.408925, float(response.text), delta=5)

    def test_add_ticket(self):
        ticket = self.TEST_FORM.copy()
        ticket.update({"price": 185.408925, "closed": False})
        id_ = self.client.post("/tickets/add", headers=self.authorize("office", TEST_DEFAULT_PASSWORD), json=ticket).text.replace('"', '')
        self.assertEqual(1, CollectionProvider.tickets().count_documents({"_id": ObjectId(id_)}))
