import sys
from unittest.mock import AsyncMock

import pytest

from shared.database import DatabaseManager
from shared.redis_client import RedisClient


@pytest.fixture(autouse=True)
def disable_external_services(monkeypatch):
    """Disable real database and Redis connections during tests."""
    monkeypatch.setattr(DatabaseManager, "create_tables", AsyncMock(return_value=None))
    monkeypatch.setattr(RedisClient, "connect", AsyncMock(return_value=None))
    monkeypatch.setattr(RedisClient, "disconnect", AsyncMock(return_value=None))
    yield


@pytest.fixture(autouse=True)
def patch_app_sys_path(monkeypatch):
    """Intercept /app path insertion in service app modules and redirect it to the backend root."""
    backend_root = str(__import__("pathlib").Path(__file__).resolve().parents[1])

    class BackendPathList(list):
        def insert(self, index, path):
            if path == "/app":
                path = backend_root
            super().insert(index, path)

    monkeypatch.setattr(sys, "path", BackendPathList(sys.path))
    yield
