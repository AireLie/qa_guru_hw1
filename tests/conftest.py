import os
import pytest
import dotenv
import json

from pathlib import Path

@pytest.fixture(autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture
def app_url():
    url = os.getenv("APP_URL")
    if not url:
        pytest.skip("Set APP_URL in .env file to run tests")
    return url


@pytest.fixture
def test_users():
    file_path = Path(__file__).parent.parent / "data" / "users.json"
    with open(file_path, "r") as f:
        return json.load(f)


@pytest.fixture
def total_users_count(test_users):
    return len(test_users)
