"""Feature A — Due dates + overdue filter tests."""

from datetime import date, timedelta


def yesterday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_create_task_with_due_date(client, make_task):
    task = make_task("Pay bill", due_date=tomorrow())
    assert task["due_date"] == tomorrow()


def test_due_date_persists_after_update(client, make_task):
    task = make_task("Pay bill", due_date=tomorrow())
    res = client.patch(f"/tasks/{task['id']}", json={"title": "Pay bill updated"})
    assert res.status_code == 200
    assert res.json()["due_date"] == tomorrow()


def test_overdue_filter_returns_overdue_tasks(client, make_task):
    make_task("Overdue task", due_date=yesterday())
    make_task("Future task",  due_date=tomorrow())
    res = client.get("/tasks?overdue=true")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "Overdue task"


def test_overdue_filter_excludes_done_tasks(client, make_task):
    """Break test: a done task should not appear as overdue even if past due."""
    task = make_task("Done overdue", due_date=yesterday())
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task['id']}", json={"status": "Done"})
    res = client.get("/tasks?overdue=true")
    assert res.json() == []


def test_overdue_filter_no_due_date_excluded(client, make_task):
    """Break test: tasks with no due_date should not appear in overdue filter."""
    make_task("No due date")
    res = client.get("/tasks?overdue=true")
    assert res.json() == []


def test_update_due_date(client, make_task):
    task = make_task("Task", due_date=yesterday())
    res = client.patch(f"/tasks/{task['id']}", json={"due_date": tomorrow()})
    assert res.status_code == 200
    assert res.json()["due_date"] == tomorrow()


def test_clear_due_date(client, make_task):
    task = make_task("Task", due_date=tomorrow())
    res = client.patch(f"/tasks/{task['id']}", json={"due_date": None})
    assert res.status_code == 200
    assert res.json()["due_date"] is None


def test_overdue_filter_false_returns_all(client, make_task):
    make_task("Overdue", due_date=yesterday())
    make_task("Future",  due_date=tomorrow())
    res = client.get("/tasks?overdue=false")
    # overdue=false means don't filter — return all
    assert len(res.json()) == 2


# ── Validation / break tests ──────────────────────────────────────────────────

def test_invalid_due_date_format_rejected(client):
    """Break test: a malformed due_date string is rejected on create."""
    res = client.post("/tasks", json={"title": "X", "due_date": "not-a-date"})
    assert res.status_code == 422


def test_invalid_due_date_format_rejected_on_update(client, make_task):
    """Break test: a malformed due_date string is rejected on update."""
    task = make_task("Task", due_date=tomorrow())
    res = client.patch(f"/tasks/{task['id']}", json={"due_date": "31-12-2026"})
    assert res.status_code == 422
