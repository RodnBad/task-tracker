# Release Evidence — End-of-Course Project

Baseline check, CI verification, Docker verification, and a claim-vs-reality check of the README — rebuilt after instructor feedback on the first submission flagged that this file was out of date and incomplete. Every section below reflects the actual final repository state, verified directly rather than restated from memory.

---

## Baseline Check

**Backend start command** (exact command from `README.md`):
```
uvicorn app.main:app --reload
```
Output:
```
INFO:     Will watch for changes in these directories: [...task-tracker']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...] using WatchFiles
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Observed `/health` result:**
```
$ curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/health
{"status":"ok"}
HTTP 200
```
(`GET /` was also checked and returns the same `{"status":"ok"}` / `200` — kept for backward compatibility, `/health` is the dedicated one used by the Dockerfile `HEALTHCHECK`.)

**Frontend opening method:** `frontend/index.html`, as documented in the README, is a static file with no build step. It was served from a local static file server for automated verification (browser tooling in this environment renders raw `file://` paths as static snapshots rather than executing them); this exercises the identical HTML/CSS/JS a double-click open would run. The page loaded with zero console errors and the board rendered correctly.

**Kanban create/edit flow confirmed working end-to-end:**
1. Clicked **+ New Task**, entered a title, saved → `POST /tasks` returned `201`, card appeared in the **To Do** column immediately.
2. Deleted the test task afterward (`DELETE /tasks/{id}` → `204`) to leave the board clean.

No regressions in the base CRUD flow from this branch's changes.

---

## Test Suite — Final State

```
pytest -v
```
**Result: 63 passed, 0 failed.**
- `test_tasks.py` — 39 tests
- `test_due_dates.py` — 10 tests
- `test_tags.py` — 14 tests

### How this number got here (accurate history, corrected from the first submission)
The first submission's release evidence said 54 and stopped there. The real progression across this branch's work:

| Count | What changed |
|---|---|
| 53 | Baseline inherited from `mid-course-project` (confirmed unchanged at the start of this branch). |
| 54 | Added `test_health_endpoint` for the new `GET /health` route (Part B). |
| 56 | Part C security review found and fixed two real bugs — stored XSS via unescaped `tags` in `frontend/index.html`, and `assignee` accepting whitespace-only values instead of normalizing to "unassigned" — each with a regression test (`test_whitespace_only_assignee_normalized_to_none`, `test_assignee_is_trimmed`). This was the state of the *first, "Not Met" submission*. |
| **63** | Instructor review of that submission found a third, more serious bug: `PATCH` accepted an explicit `null` for required fields (`status`, `title`, `description`, `priority`, `tags`), corrupting the task and — for `status` — bypassing transition validation entirely (confirmed: `PATCH {"status": null}` returned `200` and set the task's status to `null`, which matches no Kanban column). Fixed with a `model_validator` on `TaskUpdate`; 7 new regression tests added (one per required field rejecting null, plus two confirming `assignee`/`due_date` — the two genuinely nullable fields — still correctly accept null). **This is the current, final count.** |

Full narrative and grading of each finding: [`docs/final-ai-review.md`](final-ai-review.md).

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

`docker` job (`needs: test`, only runs after tests pass):

| Check | Evidence |
|---|---|
| Image builds | `docker build -t task-tracker .` |
| Container runs | `docker run -d -p 8000:8000 --name task-tracker-test task-tracker` |
| `/health` returns 200 | Polls `curl -sf http://localhost:8000/health` up to 15s, fails the job (and dumps container logs) if it never succeeds |
| Runs as non-root | `docker exec task-tracker-test whoami` — job fails if the result is `root` |

**Why this job exists:** Docker isn't installed on this development machine (`docker --version` → `command not found`), so `docker build`/`docker run` can't be verified locally. This CI job builds and runs the real image on every push using GitHub Actions' built-in Docker support, so "it builds, runs, and passes its health check" is machine-verified, not a claim.

### Final commit's actual run result

Retrieved directly from GitHub after pushing the resubmission commit `509081f` (this exact file, minus this section, was part of that push):

**Run:** [CI #3](https://github.com/RodnBad/task-tracker/actions/runs/29691732399) — commit `509081f`, branch `final-project`, triggered by push.
**Status:** ✅ Success — total duration **1m 16s**.

| Job | Conclusion | Duration |
|---|---|---|
| `test` | ✅ success | 14s |
| `docker` | ✅ success | 13s |

`docker` job step-by-step (confirmed via the GitHub Actions API, `GET /repos/RodnBad/task-tracker/actions/runs/29691732399/jobs`):

| Step | Conclusion |
|---|---|
| Checkout code | ✅ success |
| Build image | ✅ success |
| Run container | ✅ success |
| Wait for `/health` to return 200 | ✅ success |
| Confirm the process runs as a non-root user | ✅ success |
| Stop and remove container | ✅ success |

This is the actual, final, verifiable state of the submitted commit — not a description of what the workflow is supposed to do.

---

## Dockerfile Review

`Dockerfile`:
- **Multi-stage:** `builder` stage (installs dependencies to `/install`) → slim runtime stage (`python:3.12-slim`, copies only the installed packages + `app/`).
- **Non-root:** `RUN adduser --disabled-password --gecos "" appuser` then `USER appuser` before `CMD`.
- **HEALTHCHECK:** probes `GET /health` via Python's `urllib` (no `curl` in the slim image, avoids installing one just for this).

`.dockerignore`: `.git/`, `.gitignore`, `.venv/`, `venv/`, `.pytest_cache/`, `__pycache__/`, `.env`, test/doc/frontend folders.

---

## Claim-vs-Reality: README

| Claim | Reality | Result |
|---|---|---|
| Test count | Now says 63 — matches `pytest -v` exactly | ✅ Corrected |
| API table lists `GET /health` | Confirmed present in `app/main.py` | ✅ Accurate |
| "PATCH ... only send fields you're changing" | Confirmed: `update_dict = {k: getattr(payload, k) for k in payload.model_fields_set}` only applies fields actually present in the request | ✅ Accurate |
| "Invalid status transitions return 422" | Confirmed in `app/main.py` | ✅ Accurate |
| CORS scoped, not `*` | Confirmed: `allow_origins=[...]` lists specific origins | ✅ Accurate |
| `docs/midcourse/verification.md` per-file test breakdown | Was previously wrong (test_tasks.py/test_tags.py counts swapped); corrected in that file, noted there | ✅ Corrected |

---

## Secrets Scan

Confirmed no secrets/credentials/tokens/production data anywhere in the tracked repo:
```
git ls-tree -r --name-only final-project | grep -iE "\.env|secret|credential|token|\.pem|\.key|password"
# (no output)
git grep -inE "api[_-]?key|secret[_-]?key|password\s*=|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----|Bearer [A-Za-z0-9._-]{20,}" final-project -- .
# (no output)
```
`.gitignore` excludes `.env`/`.env.*`; no such file exists anywhere in the working tree.
