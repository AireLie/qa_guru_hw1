import json
import sys
from http import HTTPStatus
from math import ceil
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination


try:
    # Попытка относительного импорта (при запуске как модуля)
    from app.User import User, UserCreate, LoginData, Token
    from app.app_status import AppStatus
except ImportError:
    # Абсолютный импорт (при прямом запуске файла)
    from user import User, UserCreate, LoginData, Token
    from app_status import AppStatus

app = FastAPI()
users: List[User] = []


class CustomPage(Page[User]):
    pages: int


def load_users():
    """Загружает пользователей из JSON файла"""
    global users
    file_path = Path(__file__).parent.parent / "data" / "users.json"
    with open(file_path, "r") as f:
        users_data = json.load(f)
        users = [User(**user) for user in users_data]


def custom_paginate(sequence: List[User], page: int = 1, size: int = 10) -> CustomPage:
    """Реализация пагинации с расчетом количества страниц"""
    total = len(sequence)
    start = (page - 1) * size
    end = start + size
    items = sequence[start:end]

    return CustomPage(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if size else 1
    )


@app.get("/status", status_code=HTTPStatus.OK)
def status() -> dict:
    """Проверка статуса сервиса"""
    return {"status": "ok"}


@app.get("/api/status", status_code=HTTPStatus.OK)
def app_status() -> AppStatus:
    """Получение статуса приложения"""
    try:
        # Проверяем доступность данных
        if not users:
            load_users()
        # Проверяем что данные загружены и валидны
        if users and all(isinstance(u, User) for u in users):
            return AppStatus(users=True)
        return AppStatus(users=False)
    except Exception as e:
        print(f"Error checking app status: {e}")
        return AppStatus(users=False)


@app.get("/api/users", response_model=CustomPage)
def get_users(page: int = 1, size: int = 10):
    """Получение списка пользователей с пагинацией"""
    return custom_paginate(users, page, size)


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Получение пользователя по ID"""
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id"
        )

    user = next((u for u in users if u.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found"
        )
    return user


@app.post("/api/users", response_model=User, status_code=HTTPStatus.CREATED)
def create_user(user: UserCreate) -> User:
    """Создание нового пользователя"""
    new_id = max(u.id for u in users) + 1 if users else 1
    new_user = User(
        id=new_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar=user.avatar
    )
    users.append(new_user)
    return new_user


@app.put("/api/users/{user_id}", response_model=User)
def update_user(user_id: int, user_data: User) -> User:
    """Обновление пользователя"""
    if user_id != user_data.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User ID mismatch"
        )

    for i, user in enumerate(users):
        if user.id == user_id:
            users[i] = user_data
            return user_data

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="User not found"
    )


@app.delete("/api/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    """Удаление пользователя"""
    global users
    users = [u for u in users if u.id != user_id]


@app.post("/api/login", response_model=Token)
def login(credentials: LoginData) -> Token:
    """Аутентификация пользователя"""
    if credentials.email == "eve.holt@reqres.in" and credentials.password == "cityslicka":
        return Token(token="QpwL5tke4Pnpja7X4")
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Bad credentials"
    )


@app.post("/api/register", response_model=Token)
def register(user: UserCreate) -> Token:
    """Регистрация нового пользователя"""
    new_id = max(u.id for u in users) + 1 if users else 1
    new_user = User(
        id=new_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar=user.avatar
    )
    users.append(new_user)
    return Token(token="QpwL5tke4Pnpja7X4")


if __name__ == "__main__":
    # Добавляем путь к родительской директории в PYTHONPATH
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Инициализация
    load_users()
    print(f"Loaded {len(users)} users")
    add_pagination(app)

    # Запуск сервера
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)