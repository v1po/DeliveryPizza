import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

backend_root = Path(__file__).resolve().parents[1]
backend_src = backend_root / "src"

if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from shared.database import DatabaseManager  # noqa: E402
from shared.redis_client import RedisClient  # noqa: E402


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

    class BackendPathList(list):
        def insert(self, index, path):
            if path == "/app":
                path = backend_src
            super().insert(index, path)

    monkeypatch.setattr(sys, "path", BackendPathList(sys.path))
    yield
