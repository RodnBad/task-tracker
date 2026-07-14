# Release Evidence — End-of-Course Project

Baseline check, CI verification, Docker verification, and a claim-vs-reality check of the README, done on the `final-project` branch before any release-readiness changes were made.

---

## Baseline Check

Before making any changes on this branch, confirmed the app and test suite from `mid-course-project` still worked:

```
pytest -q
```
```
53 passed in 1.00s
```

No regressions inherited from `mid-course-project`. This branch then added a `GET /health` endpoint, a `docker` CI job, and this documentation — no product features.

---

## CI Pipeline Evidence

`.github/workflows/ci.yml`, `test` job:

| Check | Evidence |
|---|---|
| Triggers on push and pull_request | `on: push: branches: ["**"]` and `on: pull_request: branches: ["**"]` |
| Pinned Python version | `python-version: "3.12"` via `actions/setup-python@v5` |
| Installs project dependencies | `pip install -r requirements-dev.txt` |
| Runs the real test suite | `pytest -v --tb=short` |
| No failure-swallowing | No `continue-on-error`, no `\|\| true`, no `--exitfirst`/skip flags anywhere in the workflow |

New `docker` job (`needs: test`, only runs after tests pass):

| Check | Evidence |
|---|---|
| Image builds | `docker build -t task-tracker .` |
| Container runs | `docker run -d -p 8000:8000 --name task-tracker-test task-tracker` |
| `/health` returns 200 | Polls `curl -sf http://localhost:8000/health` up to 15s, fails the job (and dumps container logs) if it never succeeds |
| Runs as non-root | `docker exec task-tracker-test whoami` — job fails if the result is `root` |

**Why this job exists:** Docker isn't installed on this development machine (`docker --version` → `command not found`), so `docker build`/`docker run` couldn't be verified locally. Rather than just asserting the Dockerfile is correct, this CI job actually builds and runs the real image on every push, using GitHub Actions' built-in Docker support — so "it builds, runs, and passes its health check" is machine-verified, not a claim. Check the **Actions** tab on GitHub for the `docker` job's pass/fail status and logs after this branch is pushed.

---

## Dockerfile Review

`Dockerfile`:
- **Multi-stage:** `builder` stage (installs dependencies to `/install`) → slim runtime stage (`python:3.12-slim`, copies only the installed packages + `app/`).
- **Non-root:** `RUN adduser --disabled-password --gecos "" appuser` then `USER appuser` before `CMD`.
- **HEALTHCHECK:** added this branch — probes `GET /health` via Python's `urllib` (no `curl` in the slim image, avoids installing one just for this).

`.dockerignore` — added this branch: `.git/`, `.gitignore`, `.venv/`, `venv/`, `.pytest_cache/` (previously missing; only `__pycache__/`, `.env`, test/doc/frontend folders were excluded).

---

## Claim-vs-Reality: README

Checked every concrete claim in `README.md` against the actual code, corrected what didn't match:

| Claim | Reality | Result |
|---|---|---|
| "Expected: 53 tests, all passing" | Adding `test_health_endpoint` (for the new `/health` route) brought the count to 54 | ❌ Stale — corrected to 54 |
| API table listed only `GET /` for health | `GET /health` now also exists | ❌ Missing row — added |
| Docker section didn't mention the health check or non-root user | Both are real, verifiable properties of the image | ⚠️ Incomplete — added a line describing them and pointing to this file |
| "PATCH /tasks/{id} ... only send fields you're changing" | Confirmed: `update_dict = {k: getattr(payload, k) for k in payload.model_fields_set}` in `app/main.py` only applies fields actually present in the request body | ✅ Accurate |
| "Invalid status transitions return 422" | Confirmed: `app/main.py` raises `HTTPException(status_code=422, ...)` in `update_task` | ✅ Accurate |
| "CORS is scoped to common local dev origins ... rather than `*`" | Confirmed: `allow_origins=[...]` lists specific origins, no wildcard | ✅ Accurate |
| `docs/midcourse/verification.md` listed `test_tasks.py — 30 tests`, `test_tags.py — 13 tests` | Actual (via `pytest --collect-only`, pre-this-branch): `test_tasks.py` had 29, `test_tags.py` had 14 — the two counts were swapped. Total of 53 happened to still be correct | ❌ Wrong breakdown — corrected in that file |

---

## Test Suite

```
pytest -v
```
**Result:** 54 passed, 0 failed (test_tasks.py 30, test_due_dates.py 10, test_tags.py 14).
