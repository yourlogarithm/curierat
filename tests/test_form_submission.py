from unittest import TestCase
from fastapi.testclient import TestClient
from constants import TEST_DEFAULT_PASSWORD
from main import app

client = TestClient(app)


class FormSubmissionTest(TestCase):
    def test_submit_form(self):
        access_token = client.post("/token", data={"username": "office", "password": TEST_DEFAULT_PASSWORD}).json()['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/packages/submit_form", headers=headers, json={
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
            "category": 0
        })
        self.assertAlmostEqual(185.408925, float(response.text), delta=5)

    def test_confirm_ticket(self):
        response = client.post("/confirm_ticket", json={
            "ticket_id": "5f6e1a1c1b6d7a2a8a2b0c6d",
            "client": ""
        })
