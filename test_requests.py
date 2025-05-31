import requests
import json
import pytest

base_url = "http://0.0.0.0:8000/api"

with open("data.json", "r") as read_file:
    users_data = json.load(read_file)


def test_get_user():
    user_id = "2"
    url = f"{base_url}/users/{user_id}"

    expected_data = users_data[user_id]

    response = requests.get(url)
    body = response.json()

    assert body['id'] == expected_data['id']
    assert body['email'] == expected_data['email']


def test_create_user():
    user = {"id": 4, "email": "test.user@test.com"}
    url = f"{base_url}/users"

    response = requests.post(url, json=user)
    body = response.json()

    assert body == user


def test_update_user():
    user_id = "2"
    url = f"{base_url}/users/{user_id}"
    updated_data = {"id": 2, "email": "updated.user@test.com"}

    response = requests.put(url, json=updated_data)
    body = response.json()

    assert body == updated_data


def test_delete_user():
    # Load data from data.json
    with open('data.json') as f:
        data = json.load(f)

    # Check if user with user_id = "3" exists
    user_exists = "3" in data

    if user_exists:
        user_id = "3"
        url = f"{base_url}/users/{user_id}"

        response = requests.delete(url)
        assert response.status_code == 200
    else:
        pytest.skip("User with id '3' does not exist in data.json")


def test_login():
    url = f"{base_url}/login"
    credentials = {"email": "eve.holt@reqres.in", "password": "cityslicka"}

    response = requests.post(url, json=credentials)
    body = response.json()

    assert "token" in body


def test_get_non_existent_user():
    user_id = "1000"
    url = f"{base_url}/users/{user_id}"

    response = requests.get(url)
    body = response.json()

    assert response.status_code == 404
    assert body["detail"] == "User not found"


def test_update_non_existent_user():
    user_id = "1000"
    url = f"{base_url}/users/{user_id}"
    updated_data = {"id": 1000, "email": "non.existent.user@test.com"}

    response = requests.put(url, json=updated_data)
    body = response.json()

    assert response.status_code == 404
    assert body["detail"] == "User not found"


def test_delete_non_existent_user():
    user_id = "1000"
    url = f"{base_url}/users/{user_id}"

    response = requests.delete(url)
    body = response.json()
    assert response.status_code == 404
    assert body["detail"] == "User not found"


def test_login_with_wrong_credentials():
    url = f"{base_url}/login"
    credentials = {"email": "wrong.email@test.com", "password": "wrongpassword"}

    response = requests.post(url, json=credentials)
    body = response.json()

    assert response.status_code == 401
    assert body["detail"] == "Bad credentials"
