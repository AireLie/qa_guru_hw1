import pytest
import requests
from http import HTTPStatus


def test_get_existing_user(app_url, test_users):
    test_user = test_users[0]
    response = requests.get(f"{app_url}/api/users/{test_user['id']}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == test_user["id"]


def test_get_invalid_user_id(app_url):
    response = requests.get(f"{app_url}/api/users/0")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_nonexistent_user(app_url):
    response = requests.get(f"{app_url}/api/users/9999")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_user(app_url):
    new_user = {
        "email": "new.user@example.com",
        "first_name": "New",
        "last_name": "User",
        "avatar": "https://example.com/avatar.jpg",
        "password": "password"
    }
    response = requests.post(f"{app_url}/api/users", json=new_user)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["email"] == new_user["email"]


def test_update_user(app_url):
    updated_data = {
        "id": 2,
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
        "avatar": "https://example.com/updated.jpg"
    }
    response = requests.put(f"{app_url}/api/users/2", json=updated_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == "updated@example.com"


def test_delete_user(app_url):
    # First create a test user
    test_user = {
        "email": "to.delete@example.com",
        "first_name": "ToDelete",
        "last_name": "User",
        "avatar": "https://example.com/delete.jpg",
        "password": "password"
    }
    create_resp = requests.post(f"{app_url}/api/users", json=test_user)
    user_id = create_resp.json()["id"]

    # Now delete it
    delete_resp = requests.delete(f"{app_url}/api/users/{user_id}")
    assert delete_resp.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    verify_response = requests.get(f"{app_url}/api/users/{user_id}")
    assert verify_response.status_code == HTTPStatus.NOT_FOUND


def test_login_failure(app_url):
    response = requests.post(
        f"{app_url}/api/login",
        json={"email": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
