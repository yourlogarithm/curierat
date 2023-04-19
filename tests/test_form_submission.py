from unittest import TestCase

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class FormSubmissionTest(TestCase):

    def test_send_form(self):
        access_token = client.post("/token", data={"username": "nelu.dragan", "password": "password"}).json()['access_token']
        response = client.post("/form", json={
            "sender_contact": {
                "first_name": "Vlad-Sebastian",
                "last_name": "Cretu",
                "email": "sebastiancretu03@gmail.com",
                "phone": "0751234567"
            },
            "receiver_contact": {
                "first_name": "Nelu",
                "last_name": "Dragan",
                "email": "dragan.nelu123@gmail.com",
                "phone": "0785123456"
            },
            "office": "Timisoara",
            "destination": "Bucuresti",
            "weight": 1.5,
            "category": "fragile"
        })
        self.assertAlmostEqual(185.408925, float(response.text), delta=5)

    # def test_confirm_ticket(self):
    #     response = client.post("/confirm_ticket", json={
    #         "ticket_id": "5f6e1a1c1b6d7a2a8a2b0c6d",
    #         "client": "
