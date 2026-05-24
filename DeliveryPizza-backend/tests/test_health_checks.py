import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def load_service_app(service_name: str):
    service_root = BACKEND_ROOT / "services" / service_name
    app_dir = service_root / "app"
    package_name = f"{service_name}_app"
    module_name = f"{package_name}.main"

    pkg = types.ModuleType(package_name)
    pkg.__path__ = [str(app_dir)]
    sys.modules[package_name] = pkg

    spec = importlib.util.spec_from_file_location(
        module_name,
        app_dir / "main.py",
        submodule_search_locations=[str(app_dir)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module.app


def make_client(app):
    return TestClient(app)


def test_auth_health_endpoint():
    auth_app = load_service_app("auth")
    with make_client(auth_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "auth"}


def test_catalog_health_endpoint():
    catalog_app = load_service_app("catalog")
    with make_client(catalog_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "catalog"}


def test_gateway_health_endpoint():
    gateway_app = load_service_app("gateway")
    with make_client(gateway_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "gateway"
    assert "services" in payload
    assert payload["services"]["auth"].startswith("http")


def test_gateway_services_status_unreachable(monkeypatch):
    gateway_app = load_service_app("gateway")

    async def fake_request(*args, **kwargs):
        raise httpx.ConnectError("service unavailable")

    proxy_module = __import__("gateway_app.proxy", fromlist=["proxy"])
    monkeypatch.setattr(
        proxy_module.httpx.AsyncClient, "request", AsyncMock(side_effect=fake_request)
    )

    with make_client(gateway_app) as client:
        response = client.get("/services/status")

    assert response.status_code == 200
    services = response.json()["services"]
    assert services["auth"]["status"] == "unreachable"
    assert services["catalog"]["status"] == "unreachable"
    assert services["order"]["status"] == "unreachable"
