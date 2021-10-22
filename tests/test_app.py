import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


@pytest.fixture
def fake_user():
    data = {
              "email": "user@example.com",
              "password": "string",
              "first_name": "string",
              "last_name": "string",
              "company_name": "string",
              "address": {
                "address": "string",
                "zip_code": 0,
                "city": "string"
              },
              "siret": "string",
              "intracom_vat": "string",
              "logo": "string",
              "rib": {
                "name": "string",
                "iban": "string",
                "bic": "string"
              }
            }
    return data


def test_read_user_me():
    with TestClient(app) as client:
        response = client.get('/users/me/')
        assert response.status_code == 401


# def test_user_register(fake_user):
#     with TestClient(app) as client:
#         response = client.post('/auth/register', json=fake_user)
#     assert response.status_code == 201
#     assert response.json() == {}
