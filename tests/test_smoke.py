import pytest
import requests
from http import HTTPStatus
from math import ceil


def test_status_check(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


def test_app_status(app_url):
    """Тест статуса приложения с проверкой загрузки пользователей"""
    response = requests.get(f"{app_url}/api/status")
    assert response.status_code == HTTPStatus.OK

    status_data = response.json()
    assert "users" in status_data

    # Проверяем что статус соответствует действительности
    users_response = requests.get(f"{app_url}/api/users")
    actual_users_status = len(users_response.json()["items"]) > 0
    assert status_data["users"] == actual_users_status


@pytest.mark.parametrize("page_size", [1, 3, 5])
def test_users_pagination_structure(app_url, page_size):
    response = requests.get(f"{app_url}/api/users", params={"page": 1, "size": page_size})
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    required_keys = ["items", "total", "page", "size", "pages"]
    for key in required_keys:
        assert key in data

    assert len(data["items"]) <= page_size
    assert data["page"] == 1
    assert data["size"] == page_size
    assert data["pages"] == ceil(data["total"] / page_size)


def test_login_success(app_url):
    response = requests.post(
        f"{app_url}/api/login",
        json={"email": "eve.holt@reqres.in", "password": "cityslicka"}
    )
    assert response.status_code == HTTPStatus.OK
    assert "token" in response.json()


def test_register_success(app_url):
    response = requests.post(
        f"{app_url}/api/register",
        json={
            "email": "new.user@example.com",
            "first_name": "New",
            "last_name": "User",
            "avatar": "https://example.com/avatar.jpg",
            "password": "password"
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert "token" in response.json()
