"""Feature B — Tags / labels tests."""


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_create_task_with_tags(client, make_task):
    task = make_task("Tagged task", tags=["frontend", "urgent"])
    assert task["tags"] == ["frontend", "urgent"]


def test_create_task_no_tags_defaults_empty(client, make_task):
    task = make_task("No tags")
    assert task["tags"] == []


def test_tag_filter_returns_matching_tasks(client, make_task):
    make_task("Frontend task", tags=["frontend", "bug"])
    make_task("Backend task",  tags=["backend"])
    res = client.get("/tasks?tag=frontend")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "Frontend task"


def test_tag_filter_no_match_returns_empty(client, make_task):
    """Break test: filtering by a tag no task has returns empty list."""
    make_task("Task", tags=["backend"])
    res = client.get("/tasks?tag=nonexistent")
    assert res.json() == []


def test_update_tags(client, make_task):
    task = make_task("Task", tags=["old"])
    res = client.patch(f"/tasks/{task['id']}", json={"tags": ["new", "updated"]})
    assert res.status_code == 200
    assert res.json()["tags"] == ["new", "updated"]


def test_clear_tags(client, make_task):
    task = make_task("Task", tags=["a", "b"])
    res = client.patch(f"/tasks/{task['id']}", json={"tags": []})
    assert res.status_code == 200
    assert res.json()["tags"] == []


def test_combined_filter_tag_and_overdue(client, make_task):
    """Combine tag + overdue filters — only tasks matching both should return."""
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow  = (date.today() + timedelta(days=1)).isoformat()

    make_task("Match",    due_date=yesterday, tags=["bug"])
    make_task("No tag",   due_date=yesterday, tags=["feature"])
    make_task("No overdue", due_date=tomorrow, tags=["bug"])

    res = client.get("/tasks?overdue=true&tag=bug")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "Match"


def test_multiple_tasks_same_tag(client, make_task):
    """All tasks with the same tag should be returned."""
    make_task("A", tags=["shared"])
    make_task("B", tags=["shared"])
    make_task("C", tags=["other"])
    res = client.get("/tasks?tag=shared")
    assert len(res.json()) == 2


def test_preserve_tags_after_unrelated_update(client, make_task):
    """Updating title should not touch existing tags."""
    task = make_task("Task", tags=["keep", "me"])
    res = client.patch(f"/tasks/{task['id']}", json={"title": "Renamed"})
    assert res.status_code == 200
    assert res.json()["tags"] == ["keep", "me"]


# ── Validation / break tests ──────────────────────────────────────────────────

def test_reject_empty_tag(client):
    """Break test: an empty-string tag is rejected on create."""
    res = client.post("/tasks", json={"title": "X", "tags": ["valid", ""]})
    assert res.status_code == 422


def test_reject_whitespace_only_tag(client):
    """Break test: a whitespace-only tag is rejected on create."""
    res = client.post("/tasks", json={"title": "X", "tags": ["   "]})
    assert res.status_code == 422


def test_tags_are_trimmed(client, make_task):
    """Leading/trailing whitespace is stripped from accepted tags."""
    task = make_task("Task", tags=["  bug  ", "urgent"])
    assert task["tags"] == ["bug", "urgent"]


def test_reject_too_many_tags(client):
    """Break test: more than MAX_TAGS tags is rejected."""
    res = client.post("/tasks", json={"title": "X", "tags": [f"tag{i}" for i in range(11)]})
    assert res.status_code == 422


def test_reject_empty_tag_on_update(client, make_task):
    """Break test: updating with an empty tag is rejected."""
    task = make_task("Task", tags=["ok"])
    res = client.patch(f"/tasks/{task['id']}", json={"tags": ["ok", ""]})
    assert res.status_code == 422
