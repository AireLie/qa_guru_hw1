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

    assert response.json()["users"] is True


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
