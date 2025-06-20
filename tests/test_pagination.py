import pytest
import requests
from http import HTTPStatus
from math import ceil
from typing import Set


def test_pagination_structure_validation(app_url):
    """Тест структуры ответа с валидацией через Pydantic"""
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK

    # Проверяем структуру через импорт модели Page[User]
    try:
        from app.main import Page, User
    except ImportError:
        from main import Page, User

    # Валидация структуры ответа
    page_data = Page[User].parse_obj(response.json())
    assert page_data.items is not None
    assert page_data.total is not None
    assert page_data.page is not None
    assert page_data.size is not None
    assert page_data.pages is not None


@pytest.mark.parametrize("page_size", [1, 3, 5, 6, 10])
def test_pagination_page_size(app_url, test_users, page_size):
    """Тест пагинации с разными размерами страниц"""
    total_users = len(test_users)
    expected_pages = ceil(total_users / page_size)
    expected_items = min(page_size, total_users)

    response = requests.get(f"{app_url}/api/users", params={"size": page_size})
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Проверяем точное количество элементов
    assert len(data["items"]) == expected_items
    assert data["total"] == total_users
    assert data["pages"] == expected_pages
    assert data["size"] == page_size
    assert data["page"] == 1


@pytest.mark.parametrize("page,size", [
    (1, 2), (2, 2), (3, 2),  # Крайние случаи
    (1, 3), (2, 3), (3, 3),  # Разные комбинации
    (1, 6), (1, 10)  # Размер больше, чем данных
])
def test_pagination_different_pages(app_url, test_users, page, size):
    """Тест, что разные страницы возвращают разные данные"""
    total_users = len(test_users)
    expected_pages = ceil(total_users / size)

    # Получаем данные для страницы
    response = requests.get(f"{app_url}/api/users", params={"page": page, "size": size})
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Проверяем ожидаемое количество элементов
    if page < expected_pages:
        assert len(data["items"]) == size
    elif page == expected_pages:
        assert len(data["items"]) == (total_users % size or size)
    else:
        assert len(data["items"]) == 0

    # Проверяем, что все элементы уникальны (нет дубликатов)
    all_ids = [item["id"] for item in data["items"]]
    assert len(all_ids) == len(set(all_ids))  # Проверка на уникальность


def test_pagination_unique_items_across_pages(app_url):
    """Тест, что элементы на разных страницах не повторяются"""
    page_size = 3
    seen_ids: Set[int] = set()

    # Проверяем первые 3 страницы (больше чем реально существует)
    for page in [1, 2, 3]:
        response = requests.get(f"{app_url}/api/users", params={"page": page, "size": page_size})
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        current_ids = {item["id"] for item in data["items"]}

        # Проверяем, что нет пересечений с уже увиденными ID
        assert seen_ids.isdisjoint(current_ids)

        # Добавляем новые ID в множество
        seen_ids.update(current_ids)


def test_pagination_edge_cases(app_url, test_users):
    """Тест граничных случаев пагинации"""
    total_users = len(test_users)

    # Страница больше, чем всего страниц
    response = requests.get(f"{app_url}/api/users", params={"page": 100, "size": 2})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["items"]) == 0

    # Размер страницы больше, чем всего элементов
    response = requests.get(f"{app_url}/api/users", params={"size": total_users + 10})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["items"]) == total_users
    assert response.json()["pages"] == 1

    # Нулевой размер страницы (должен вернуть ошибку)
    response = requests.get(f"{app_url}/api/users", params={"size": 0})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_pagination_default_values(app_url, test_users):
    """Тест значений по умолчанию"""
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Проверяем, что пагинация работает даже без параметров
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data

    # Проверяем, что все пользователи вернулись (по-умолчанию)
    assert len(data["items"]) == len(test_users)
    assert data["total"] == len(test_users)
    assert data["pages"] == 1
