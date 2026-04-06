import pytest
from fastapi.testclient import TestClient

from app.clients.github_client import fetch
from app.main import app


@pytest.fixture
def app_main():
    return app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    fetch.cache_clear()
