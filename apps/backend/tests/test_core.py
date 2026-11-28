import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import NotFoundError, register_error_handlers
from app.core.logging import JsonFormatter, request_id_ctx
from app.core.middleware import RequestIdMiddleware


class ItemIn(BaseModel):
    name: str


def build_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)
    app.add_middleware(RequestIdMiddleware)

    @app.post("/items")
    def create_item(item: ItemIn) -> ItemIn:
        return item

    @app.get("/missing")
    def missing() -> None:
        raise NotFoundError("Dataset não encontrado.")

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("segredo-interno-123")

    return app


client = TestClient(build_app(), raise_server_exceptions=False)


def test_app_error_returns_problem_details():
    response = client.get("/missing")
    body = response.json()
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["code"] == "not_found"
    assert body["detail"] == "Dataset não encontrado."
    assert body["instance"] == "/missing"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_unknown_route_is_problem_details():
    response = client.get("/nao-existe")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "http_404"


def test_validation_error_does_not_echo_input():
    response = client.post("/items", json={"name": 123456, "extra": "x"})
    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "validation_error"
    assert body["errors"]
    assert all("input" not in error for error in body["errors"])


def test_unexpected_error_does_not_leak_details():
    response = client.get("/boom")
    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
    assert "segredo-interno-123" not in response.text
    assert "Traceback" not in response.text


def test_request_id_is_generated_and_echoed():
    generated = client.get("/missing").headers["X-Request-ID"]
    assert len(generated) >= 16

    echoed = client.get("/missing", headers={"X-Request-ID": "abc-123"})
    assert echoed.headers["X-Request-ID"] == "abc-123"


@pytest.mark.parametrize("invalid", ["tem espaco e !", "x" * 65, "a/b"])
def test_invalid_request_id_is_replaced(invalid: str):
    response = client.get("/missing", headers={"X-Request-ID": invalid})
    assert response.headers["X-Request-ID"] != invalid


def test_json_formatter_includes_request_id_and_context():
    token = request_id_ctx.set("req-1")
    try:
        record = logging.LogRecord("t", logging.INFO, __file__, 1, "olá %s", ("mundo",), None)
        record.context = {"status": 200}
        data = json.loads(JsonFormatter().format(record))
    finally:
        request_id_ctx.reset(token)

    assert data["message"] == "olá mundo"
    assert data["level"] == "INFO"
    assert data["request_id"] == "req-1"
    assert data["context"] == {"status": 200}
    assert data["service"] == "backend"
