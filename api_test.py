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


def test_register_client_with_higher_access_level():
    response = client.post("/users/register_client", json={
        "username": "higher_access_level_test",
        "email": "higher_access_level_test@gmail.com",
        "fullname": "Higher Access Level Test",
        "disabled": False,
        "password": "password",
        "access_level": 3,
        "test": True
    })
    assert response.status_code == 403


def test_register_client_with_proper_access_level():
    response = client.post("/users/register_client", json={
        "username": "proper_access_level_test",
        "email": "proper_access_level_test@gmail.com",
        "fullname": "Proper Access Level Test",
        "disabled": False,
        "password": "password",
        "access_level": 0,
        "test": True
    })
    assert response.status_code == 200


def test_register_employee_as_client():
    response = client.post("/token", data={"username": "nelu.dragan", "password": "password"})
    assert response.status_code == 200

    response = client.post(
        "/users/register_employee",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
        json={"username": "client_access_level_test", "email": "client_access_level_test@gmail.com",
              "fullname": "Client Access Level Test", "disabled": False, "password": "password", "access_level": 3,
              "test": True}
    )
    assert response.status_code == 403


def test_register_employee_as_admin():
    response = client.post("/token", data={"username": "vlad-sebastian.cretu", "password": "12345"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    data = {"username": "client_access_level_test", "email": "client_access_level_test@gmail.com",
            "fullname": "Client Access Level Test", "disabled": False, "password": "password", "access_level": 0,
            "test": True}
    response = client.post("/users/register_employee", headers=headers, json=data)
    assert response.status_code == 403

    data["access_level"] = 3
    response = client.post("/users/register_employee", headers=headers, json=data)
    assert response.status_code == 200
