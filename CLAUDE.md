# CLAUDE.md — Task Tracker

## Project Overview
Task Tracker is a FastAPI-based task management app built as the running project for the AUB AI-Assisted Coding course. It includes a Kanban board frontend (vanilla JS) and a Python backend with in-memory storage.

## Architecture
- **Backend**: FastAPI + Pydantic v2, in-memory dict store (no database)
- **Frontend**: Single-file `frontend/index.html` — vanilla JS, no build step
- **Tests**: pytest + httpx TestClient

## Key Commands
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run the API server (hot reload)
uvicorn app.main:app --reload

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_due_dates.py -v
```

## Project Structure
```
app/
  main.py            # FastAPI app, all endpoints
  models.py          # Pydantic models (Task, TaskCreate, TaskUpdate, TaskStatus)
  storage.py         # In-memory store (get_all, get_by_id, save, delete, clear)
  business_rules.py  # Status transition validation
frontend/
  index.html         # Kanban board (single file, no build step)
tests/
  conftest.py        # Fixtures (client, make_task, autouse clear_storage)
  test_tasks.py      # Base CRUD + business rule tests (30 tests)
  test_due_dates.py  # Feature A: due dates + overdue filter (10 tests)
  test_tags.py       # Feature B: tags + tag filter + validation (13 tests)
docs/midcourse/      # Mid-course project documentation
```

## Data model
`Task` fields: `id`, `title`, `description`, `status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`, default `Medium`), `assignee` (optional string), `due_date` (optional date), `tags` (list of strings).
`TaskCreate`/`TaskUpdate` use `model_config = ConfigDict(extra="forbid")` — unknown fields (e.g. client-supplied `id`) are rejected with 422, not silently ignored.
Update endpoint is `PATCH /tasks/{id}`, not `PUT`. Invalid status transitions return `422`, not `400`.

## Constraints — Do NOT
- Add a real database (use in-memory storage only)
- Add authentication or authorization
- Add new Python dependencies without updating requirements.txt
- Skip transition validation when updating status
- Change the test fixture names (conftest.py is shared across all test files)

## Current State
Mid-course project complete. Features A (due dates) and B (tags) implemented.
Module 2 spec compliance fix applied (priority/assignee fields, PATCH, 422, extra=forbid,
whitespace-title rejection, scoped CORS) — verified against the official `verify_a.py` script.
All tests passing. See docs/midcourse/ for project documentation.
