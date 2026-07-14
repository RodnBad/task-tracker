# AGENTS.md — Task Tracker

Guardrails for any AI agent (Claude Code, Codex, Copilot, etc.) working in this repository.

## Stack & Commands
- **Backend**: FastAPI + Pydantic v2, in-memory dict store (no database), Python 3.12
- **Frontend**: single-file `frontend/index.html` — vanilla JS, no build step
- **Tests**: pytest + httpx `TestClient`

```bash
pip install -r requirements-dev.txt   # install
uvicorn app.main:app --reload         # run the API
pytest -v                             # run tests (expect 54 passing)
docker build -t task-tracker .        # build the container
docker run -p 8000:8000 task-tracker  # run the container
```

## Project Rules
- No real database — in-memory storage only (`app/storage.py`).
- No authentication or authorization.
- No new Python dependencies without updating `requirements.txt`.
- Never skip status-transition validation when updating a task's `status`.
- Don't rename the test fixtures in `tests/conftest.py` — shared across all test files.
- `Task` fields: `id`, `title`, `description`, `status` (`ToDo`/`InProgress`/`Done`), `priority` (`Low`/`Medium`/`High`), `assignee`, `due_date`, `tags`. `TaskCreate`/`TaskUpdate` use `extra="forbid"` — don't remove it.

## End-of-Course Project Boundaries (branch: `final-project`)
This branch is a **release check**, not a feature branch:
- **No new product features.** Do not implement comments, authentication, a production database, notifications, or unrelated UI changes.
- **`app/` and `frontend/` are protected.** Only touch them for a small, explainable bug fix, security fix, or documentation-supported correction — and record what changed and why in `docs/final-ai-review.md`.
- If you're unsure whether a change counts as a "new feature" vs. a "small fix," treat it as a feature and don't make it without asking first.
- Read `docs/midcourse/` and `docs/release-evidence.md` before assuming something isn't already documented — don't duplicate existing ADRs/decisions.

## Review Expectations
- Read the actual diff before calling anything done — don't assume a generated change is correct.
- Run `pytest -v` after every change; don't report work as finished with failing or unrun tests.
- When reviewing AI-generated code (yours or another tool's), classify each finding honestly — a finding that doesn't reproduce or doesn't apply to this project's actual scope is Noise, not Useful, even if it sounds correct in the abstract.
- Prefer verifying claims (run the command, hit the endpoint, read the file) over restating them.
