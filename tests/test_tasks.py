"""Base CRUD and business-rule tests for Task Tracker."""


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_health_endpoint(client):
    """Dedicated /health endpoint used by the Dockerfile HEALTHCHECK."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ── Create ─────────────────────────────────────────────────────────────────────

def test_create_task_minimal(client):
    res = client.post("/tasks", json={"title": "Buy milk"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "ToDo"
    assert data["priority"] == "Medium"
    assert data["assignee"] is None
    assert data["description"] == ""
    assert data["tags"] == []
    assert data["due_date"] is None
    assert "id" in data


def test_create_task_full(client):
    res = client.post("/tasks", json={
        "title": "Full task",
        "description": "A description",
        "priority": "High",
        "assignee": "Rodney",
        "due_date": "2099-12-31",
        "tags": ["backend", "urgent"],
    })
    assert res.status_code == 201
    data = res.json()
    assert data["priority"] == "High"
    assert data["assignee"] == "Rodney"
    assert data["due_date"] == "2099-12-31"
    assert data["tags"] == ["backend", "urgent"]


def test_create_task_missing_title(client):
    res = client.post("/tasks", json={"description": "no title"})
    assert res.status_code == 422


def test_create_task_empty_title(client):
    res = client.post("/tasks", json={"title": ""})
    assert res.status_code == 422


def test_create_task_whitespace_title_rejected(client):
    """Break test: a whitespace-only title is rejected."""
    res = client.post("/tasks", json={"title": "   "})
    assert res.status_code == 422


def test_create_task_title_too_long_rejected(client):
    res = client.post("/tasks", json={"title": "x" * 201})
    assert res.status_code == 422


def test_create_task_rejects_unknown_field(client):
    """Break test: extra='forbid' means unrecognized fields are rejected, not ignored."""
    res = client.post("/tasks", json={"title": "X", "made_up": "value"})
    assert res.status_code == 422


def test_create_task_id_not_client_settable(client):
    """Break test: a client-supplied id must be rejected, not silently accepted."""
    res = client.post("/tasks", json={"title": "X", "id": "abc"})
    assert res.status_code == 422


def test_create_task_invalid_priority_rejected(client):
    res = client.post("/tasks", json={"title": "X", "priority": "Urgent"})
    assert res.status_code == 422


# ── List ───────────────────────────────────────────────────────────────────────

def test_list_tasks_empty(client):
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.json() == []


def test_list_tasks_returns_all(client, make_task):
    make_task("Task 1")
    make_task("Task 2")
    res = client.get("/tasks")
    assert len(res.json()) == 2


# ── Get ────────────────────────────────────────────────────────────────────────

def test_get_task(client, make_task):
    task = make_task("Get me")
    res = client.get(f"/tasks/{task['id']}")
    assert res.status_code == 200
    assert res.json()["title"] == "Get me"


def test_get_task_not_found(client):
    res = client.get("/tasks/nonexistent-id")
    assert res.status_code == 404


# ── Update ─────────────────────────────────────────────────────────────────────

def test_update_task_title(client, make_task):
    task = make_task("Old title")
    res = client.patch(f"/tasks/{task['id']}", json={"title": "New title"})
    assert res.status_code == 200
    assert res.json()["title"] == "New title"


def test_update_task_not_found(client):
    res = client.patch("/tasks/ghost", json={"title": "X"})
    assert res.status_code == 404


def test_update_task_whitespace_title_rejected(client, make_task):
    """Break test: a whitespace-only title is rejected on update too."""
    task = make_task("Task")
    res = client.patch(f"/tasks/{task['id']}", json={"title": "   "})
    assert res.status_code == 422


def test_update_task_created_at_not_client_settable(client, make_task):
    """Break test: created_at is not a real field — extra='forbid' rejects it."""
    task = make_task("Task")
    res = client.patch(f"/tasks/{task['id']}", json={"created_at": "2025-01-01T00:00:00Z"})
    assert res.status_code == 422


def test_update_priority_and_assignee(client, make_task):
    task = make_task("Task")
    res = client.patch(f"/tasks/{task['id']}", json={"priority": "Low", "assignee": "Sam"})
    assert res.status_code == 200
    data = res.json()
    assert data["priority"] == "Low"
    assert data["assignee"] == "Sam"


def test_whitespace_only_assignee_normalized_to_none(client):
    """Found during the Part C security review: unlike title/tags, assignee had
    no validator, so a whitespace-only assignee was stored as-is instead of
    being treated as "unassigned"."""
    res = client.post("/tasks", json={"title": "X", "assignee": "   "})
    assert res.status_code == 201
    assert res.json()["assignee"] is None


def test_assignee_is_trimmed(client):
    res = client.post("/tasks", json={"title": "X", "assignee": "  Rodney  "})
    assert res.status_code == 201
    assert res.json()["assignee"] == "Rodney"


# ── Delete ─────────────────────────────────────────────────────────────────────

def test_delete_task(client, make_task):
    task = make_task("Delete me")
    res = client.delete(f"/tasks/{task['id']}")
    assert res.status_code == 204
    # confirm gone
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_delete_task_not_found(client):
    res = client.delete("/tasks/ghost")
    assert res.status_code == 404


# ── Status transitions ────────────────────────────────────────────────────────

def test_valid_transition_todo_to_in_progress(client, make_task):
    task = make_task()
    res = client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    assert res.status_code == 200
    assert res.json()["status"] == "InProgress"


def test_valid_transition_in_progress_to_done(client, make_task):
    task = make_task()
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    res = client.patch(f"/tasks/{task['id']}", json={"status": "Done"})
    assert res.status_code == 200
    assert res.json()["status"] == "Done"


def test_valid_transition_done_to_in_progress(client, make_task):
    """A completed task can be reopened."""
    task = make_task()
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task['id']}", json={"status": "Done"})
    res = client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    assert res.status_code == 200
    assert res.json()["status"] == "InProgress"


def test_invalid_transition_in_progress_to_todo(client, make_task):
    """Break test: InProgress → ToDo is not allowed (only Done → InProgress reopens)."""
    task = make_task()
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    res = client.patch(f"/tasks/{task['id']}", json={"status": "ToDo"})
    assert res.status_code == 422


def test_invalid_transition_todo_to_done(client, make_task):
    """Break test: ToDo → Done is not allowed (cannot skip InProgress)."""
    task = make_task()
    res = client.patch(f"/tasks/{task['id']}", json={"status": "Done"})
    assert res.status_code == 422


def test_invalid_transition_done_to_todo(client, make_task):
    """Break test: Done → ToDo is not allowed."""
    task = make_task()
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task['id']}", json={"status": "Done"})
    res = client.patch(f"/tasks/{task['id']}", json={"status": "ToDo"})
    assert res.status_code == 422


def test_same_status_is_rejected(client, make_task):
    """Break test: updating to the same status is a no-op and must be rejected."""
    task = make_task()
    res = client.patch(f"/tasks/{task['id']}", json={"status": "ToDo"})
    assert res.status_code == 422


def test_invalid_status_value_rejected(client, make_task):
    task = make_task()
    res = client.patch(f"/tasks/{task['id']}", json={"status": "Whatever"})
    assert res.status_code == 422
