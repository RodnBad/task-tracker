# Verification Log — Mid-Course Project

Claim-vs-reality check for each feature. Verified by running the app locally and the test suite.

---

## Feature A: Due Dates + Overdue Filter

| # | Claim | How Verified | Result |
|---|-------|-------------|--------|
| A1 | POST /tasks accepts `due_date` and stores it | `curl -X POST ... -d '{"title":"X","due_date":"2026-07-01"}'` → response includes `"due_date": "2026-07-01"` | ✅ Match |
| A2 | GET /tasks?overdue=true returns only past-due non-done tasks | Created one task with yesterday's date, one with tomorrow's. GET ?overdue=true → only yesterday's task returned | ✅ Match |
| A3 | Done tasks are excluded from overdue filter | Moved a past-due task to done. GET ?overdue=true → empty list | ✅ Match |
| A4 | Tasks with no due_date excluded from overdue filter | Created task with no due_date. GET ?overdue=true → not returned | ✅ Match |
| A5 | Overdue cards show red highlight in frontend | Opened frontend with a past-due task visible → red left border and "⚠ overdue" badge shown | ✅ Match |
| A6 | Updating due_date to null clears it | PATCH /tasks/{id} with `{"due_date": null}` → response shows `"due_date": null` | ✅ Match |
| A7 | Invalid due_date format rejected | `curl -X POST ... -d '{"title":"X","due_date":"not-a-date"}'` → `422` | ✅ Match |
| A8 | Invalid due_date format rejected on update | PUT with `{"due_date": "31-12-2026"}` → `422` | ✅ Match |

---

## Feature B: Tags / Labels

| # | Claim | How Verified | Result |
|---|-------|-------------|--------|
| B1 | POST /tasks accepts `tags` list and stores it | `curl -X POST ... -d '{"title":"X","tags":["bug","urgent"]}'` → response includes `"tags": ["bug", "urgent"]` | ✅ Match |
| B2 | Tasks default to empty tags list | POST with no `tags` field → `"tags": []` in response | ✅ Match |
| B3 | GET /tasks?tag=bug returns only tasks tagged "bug" | Created tasks with tags ["bug"] and ["feature"]. GET ?tag=bug → 1 result | ✅ Match |
| B4 | Filter by tag not present → empty list | GET /tasks?tag=nonexistent → `[]` | ✅ Match |
| B5 | PATCH /tasks/{id} with tags replaces tag list | Task has ["old"]. PATCH with `{"tags": ["new"]}` → `"tags": ["new"]` | ✅ Match |
| B6 | Combined ?overdue=true&tag=bug filter works | Created 3 tasks (see test_tags.py::test_combined_filter_tag_and_overdue). GET with both params → 1 result | ✅ Match |
| B7 | Tags shown as pills in frontend | Opened frontend → tags displayed as blue rounded badges on each card | ✅ Match |
| B8 | Empty/whitespace-only tag rejected | `curl -X POST ... -d '{"title":"X","tags":["valid",""]}'` → `422` (before the fix, this returned `201` and stored the empty tag) | ✅ Match |
| B9 | Tags are trimmed of surrounding whitespace | POST with `tags: ["  bug  "]` → response `"tags": ["bug"]` | ✅ Match |
| B10 | More than 10 tags rejected | POST with 11 tags → `422` | ✅ Match |
| B11 | Tags preserved after unrelated update | Task has `tags: ["keep","me"]`. PATCH with `{"title": "Renamed"}` → `"tags": ["keep","me"]` unchanged | ✅ Match |

---

## Break Test Evidence (before/after)

Two of the required Break Tests, showing the behavior contract before and after the fix:

**Break Test 1 — empty tag validation (`test_reject_empty_tag`)**
- Before fix: `POST /tasks {"title":"X","tags":["valid",""]}` → `201 Created`, task stored with an empty-string tag. Contract violated: spec requires "trimmed non-empty tag values."
- After fix: same request → `422 Unprocessable Entity`, `ValueError: Tags must not be empty or whitespace-only.`
- Verified manually via `curl` and via `pytest tests/test_tags.py::test_reject_empty_tag -v` (passed).

**Break Test 2 — done tasks excluded from overdue (`test_overdue_filter_excludes_done_tasks`)**
- Contract: a task past its due date must NOT appear in `?overdue=true` once its status is `done`.
- Verified: created a task with yesterday's due date, transitioned `todo → in_progress → done`, then called `GET /tasks?overdue=true` → `[]`. Confirms the filter checks `status != "done"`, not just the date.
- `pytest tests/test_due_dates.py::test_overdue_filter_excludes_done_tasks -v` → passed.

---

## Base App Correctness Fix: Status Transition Rules

Not one of the two mid-course features, but found and fixed during manual testing of this project (see [mini-adr.md](mini-adr.md), ADR-06 for details).

**Contract (per Module 2 Lecture Notes / Prompt Library / Quiz answer key):** `todo → in_progress`, `in_progress → done`, and `done → in_progress` (reopen) are the only valid transitions. `todo → done`, `done → todo`, `in_progress → todo`, and same-status no-ops must all be rejected with `400`.

- Before fix: `done → in_progress` was rejected (should have been allowed); `in_progress → todo` was allowed (should have been rejected); same-status updates always succeeded (should have been rejected).
- After fix: manually reopened a `done` task via `PUT /tasks/{id} {"status": "in_progress"}` → `200`, task now `in_progress`. Attempted `in_progress → todo` → `400`. Attempted a same-status PUT → `400`.
- `pytest tests/test_tasks.py -k transition -v` and `-k same_status` → all passing.

---

## Base App Compliance Fix: priority, assignee, PATCH, 422, extra=forbid, whitespace-title, CORS

Also not one of the two mid-course features — a fuller Module 2 spec audit (see [mini-adr.md](mini-adr.md), ADR-07). Verified two ways: the instructor's own `verify_a.py` script, and manual/live testing.

**`verify_a.py` — before and after:**
```
# Before
ImportError: cannot import name 'TaskPriority' from 'app.models'

# After
PASS: whitespace title rejected
PASS: empty title rejected
PASS: title > 200 chars rejected
PASS: defaults applied (status=ToDo, priority=Medium, description='')
PASS: extra field rejected on TaskCreate
PASS: id rejected on TaskCreate
PASS: created_at rejected on TaskUpdate
PASS: invalid status rejected
--- Part A verifications complete ---
```

**Live browser verification** (backend on `:8000`, frontend served on `:9500`):
- Created a task via the modal with Priority=High, Assignee="Rodney" → card shows `High` pill and `👤 Rodney` badge; `POST /tasks` → `201`.
- Edited the task's status to `InProgress` via the modal → `PATCH /tasks/{id}` → `200`, card moved columns.
- Created a second Low-priority task in the same column → confirmed it renders *below* the High-priority card (priority sort High→Medium→Low working).
- Attempted an invalid transition (`InProgress → ToDo`) via the modal → `PATCH` → `422`, modal stayed open and showed `"Invalid status transition: 'InProgress' → 'ToDo'. Allowed transitions: ToDo→InProgress, InProgress→Done, Done→InProgress."` — no false-success toast.

**Break Test — whitespace-only title:**
- Before fix: `POST /tasks {"title":" "}` → `201 Created` (accepted, only checked length ≥ 1, not content after stripping).
- After fix: same request → `422`, `ValueError: Title must not be empty or whitespace-only.`
- `pytest tests/test_tasks.py::test_create_task_whitespace_title_rejected -v` → passed.

**Break Test — unknown/forbidden fields:**
- Before fix: `POST /tasks {"title":"X","id":"abc"}` → `201`, the client-supplied `id` silently ignored (server generated its own).
- After fix: same request → `422` (`extra="forbid"` rejects the unrecognized `id` field on `TaskCreate`).
- `pytest tests/test_tasks.py::test_create_task_id_not_client_settable -v` → passed.

---

## Test Suite

```
pytest -v
```

**Results:**
- test_tasks.py — 30 tests passed
- test_due_dates.py — 10 tests passed
- test_tags.py — 13 tests passed
- **Total: 53 tests, 0 failures**

Baseline (before this project's changes, Modules 1-3 CRUD only): 20 tests, all passing.
