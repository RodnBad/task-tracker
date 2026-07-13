"""Base CRUD and business-rule tests for Task Tracker."""


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ── Create ─────────────────────────────────────────────────────────────────────

def test_create_task_minimal(client):
    res = client.post("/tasks", json={"title": "Buy milk"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "todo"
    assert data["description"] == ""
    assert data["tags"] == []
    assert data["due_date"] is None
    assert "id" in data


def test_create_task_full(client):
    res = client.post("/tasks", json={
        "title": "Full task",
        "description": "A description",
        "due_date": "2099-12-31",
        "tags": ["backend", "urgent"],
    })
    assert res.status_code == 201
    data = res.json()
    assert data["due_date"] == "2099-12-31"
    assert data["tags"] == ["backend", "urgent"]


def test_create_task_missing_title(client):
    res = client.post("/tasks", json={"description": "no title"})
    assert res.status_code == 422


def test_create_task_empty_title(client):
    res = client.post("/tasks", json={"title": ""})
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
    res = client.put(f"/tasks/{task['id']}", json={"title": "New title"})
    assert res.status_code == 200
    assert res.json()["title"] == "New title"


def test_update_task_not_found(client):
    res = client.put("/tasks/ghost", json={"title": "X"})
    assert res.status_code == 404


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
    res = client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_valid_transition_in_progress_to_done(client, make_task):
    task = make_task()
    client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    res = client.put(f"/tasks/{task['id']}", json={"status": "done"})
    assert res.status_code == 200
    assert res.json()["status"] == "done"


def test_valid_transition_done_to_in_progress(client, make_task):
    """A completed task can be reopened."""
    task = make_task()
    client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    client.put(f"/tasks/{task['id']}", json={"status": "done"})
    res = client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_invalid_transition_in_progress_to_todo(client, make_task):
    """Break test: in_progress → todo is not allowed (only done → in_progress reopens)."""
    task = make_task()
    client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    res = client.put(f"/tasks/{task['id']}", json={"status": "todo"})
    assert res.status_code == 400


def test_invalid_transition_todo_to_done(client, make_task):
    """Break test: todo → done is not allowed (cannot skip in_progress)."""
    task = make_task()
    res = client.put(f"/tasks/{task['id']}", json={"status": "done"})
    assert res.status_code == 400


def test_invalid_transition_done_to_todo(client, make_task):
    """Break test: done → todo is not allowed."""
    task = make_task()
    client.put(f"/tasks/{task['id']}", json={"status": "in_progress"})
    client.put(f"/tasks/{task['id']}", json={"status": "done"})
    res = client.put(f"/tasks/{task['id']}", json={"status": "todo"})
    assert res.status_code == 400


def test_same_status_is_rejected(client, make_task):
    """Break test: updating to the same status is a no-op and must be rejected."""
    task = make_task()
    res = client.put(f"/tasks/{task['id']}", json={"status": "todo"})
    assert res.status_code == 400
