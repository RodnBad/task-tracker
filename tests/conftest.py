"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def clear_storage():
    """Reset in-memory store before every test."""
    storage.clear()
    yield
    storage.clear()


@pytest.fixture
def client():
    """Return a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def make_task(client):
    """Helper: create a task and return the response JSON."""
    def _make(title="Test task", description="", due_date=None, tags=None):
        payload = {"title": title, "description": description}
        if due_date:
            payload["due_date"] = due_date
        if tags is not None:
            payload["tags"] = tags
        res = client.post("/tasks", json=payload)
        assert res.status_code == 201
        return res.json()
    return _make
