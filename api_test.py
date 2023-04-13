from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_send_form():
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
    assert response.status_code == 200
    assert response.json() == {"message": "Form received"}
