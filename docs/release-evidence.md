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
**Result: 65 passed, 0 failed.**
- `test_tasks.py` — 41 tests
- `test_due_dates.py` — 10 tests
- `test_tags.py` — 14 tests

### How this number got here (accurate history, corrected from the first submission)
The first submission's release evidence said 54 and stopped there. The real progression across this branch's work:

| Count | What changed |
|---|---|
| 53 | Baseline inherited from `mid-course-project` (confirmed unchanged at the start of this branch). |
| 54 | Added `test_health_endpoint` for the new `GET /health` route (Part B). |
| 56 | Part C security review found and fixed two real bugs — stored XSS via unescaped `tags` in `frontend/index.html`, and `assignee` accepting whitespace-only values instead of normalizing to "unassigned" — each with a regression test (`test_whitespace_only_assignee_normalized_to_none`, `test_assignee_is_trimmed`). This was the state of the *first, "Not Met" submission*. |
| 63 | Instructor review of that submission found a third, more serious bug: `PATCH` accepted an explicit `null` for required fields (`status`, `title`, `description`, `priority`, `tags`), corrupting the task and — for `status` — bypassing transition validation entirely (confirmed: `PATCH {"status": null}` returned `200` and set the task's status to `null`, which matches no Kanban column). Fixed with a `model_validator` on `TaskUpdate`; 7 new regression tests added (one per required field rejecting null, plus two confirming `assignee`/`due_date` — the two genuinely nullable fields — still correctly accept null). |
| **65** | Requested an independent adversarial review pass after the fix above (not another instructor round) — it found the same bug class survives as a Unicode edge case: a title/assignee/tag made of only zero-width characters (e.g. U+200B) passes `str.strip()` unchanged, since Python doesn't count them as whitespace. Fixed with a shared `_strip_invisible()` helper applied to all three fields; 2 new regression tests. **This is the current, final count.** |

Full narrative and grading of each finding, including what the adversarial pass tried and could *not* break: [`docs/final-ai-review.md`](final-ai-review.md).

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

### CI/Docker run results for every code-bearing commit on this branch

An independent review of the first resubmission attempt found that this section cited CI evidence for commit `509081f` while two more commits (including the actual code fix for a second bug) had already landed on top of it — the same "evidence doesn't match the real final state" problem the instructor originally raised, recurring in miniature. To avoid that happening a third time, every commit that changed `app/`, `frontend/`, or `tests/` on this branch is listed below, not just one:

| Commit | What changed | CI run | Result |
|---|---|---|---|
| `509081f` | Null-validation fix | [CI #3](https://github.com/RodnBad/task-tracker/actions/runs/29691732399) | ✅ Success, 1m 16s (test 14s, docker 13s) |
| `9e4c5fb` | Docs only (recorded the run above) — no `app/`/`tests/` changes | [CI #4](https://github.com/RodnBad/task-tracker/actions/runs/29692998702) | ✅ Success |
| `e35e63e` | Zero-width-character validation fix (`app/models.py`, `tests/test_tasks.py`) | [CI #5](https://github.com/RodnBad/task-tracker/actions/runs/29697933651) | ✅ Success, 1m 48s (test 16s, docker 22s) |

**`e35e63e` is the most recent commit that changes `app/`/`frontend/`/`tests/` as of this writing — its CI run (#5) is the one that actually reflects the current application behavior.** Full step-by-step for that run (confirmed via the GitHub Actions API, `GET /repos/RodnBad/task-tracker/actions/runs/29697933651/jobs`):

| Step | Conclusion |
|---|---|
| Checkout code | ✅ success |
| Build image | ✅ success |
| Run container | ✅ success |
| Wait for `/health` to return 200 | ✅ success |
| Confirm the process runs as a non-root user | ✅ success |
| Stop and remove container | ✅ success |

Any commits made *after* this file was last updated (e.g. to fix something this very validation pass found) will have their own run visible on the **Actions** tab on GitHub — check there for the true HEAD if this file is ever behind again.

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
| Test count | Now says 65 — matches `pytest -v` exactly | ✅ Corrected |
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
