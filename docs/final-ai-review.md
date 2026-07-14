# Final AI Review — End-of-Course Project

AI code review and security review of the codebase, done on the `final-project` branch, with every finding graded honestly rather than accepted at face value — per `AGENTS.md`'s review expectations.

---

## AGENTS.md Guardrails Confirmed

Both changes made on this branch (below) are within `AGENTS.md`'s "small bug fix / security fix" carve-out for `app/`/`frontend/`, not new product features:
- The XSS fix (`frontend/index.html`) is a one-line escaping fix to an existing render path — no new field, no new UI, no new behavior for a legitimate user.
- The `assignee` whitespace fix (`app/models.py`) brings `assignee` in line with how `title` and `tags` already behave — a consistency/correctness fix, not new functionality.

No other `app/`/`frontend/` changes were made on this branch. Everything else added (`AGENTS.md`, `docs/release-evidence.md`, this file, the `/health` endpoint, the Dockerfile `HEALTHCHECK`, the CI `docker` job) is release-readiness infrastructure, not a product feature.

---

## AI Code Review — Graded Findings

Reviewed `app/main.py`, `app/models.py`, `app/business_rules.py`, `app/storage.py`, and `frontend/index.html` in full.

| # | Finding | Grade | Reasoning |
|---|---|---|---|
| 1 | `frontend/index.html`: `title`, `description`, and `assignee` are all passed through `esc()` before being injected into card HTML, but `tags` is not (`tagsHtml = task.tags.map(g => ...)` used the raw string directly) | **Useful** | Real, reproducible bug — an inconsistency with every other user-controlled string field in the same function. Fixed (see security findings below). |
| 2 | `app/models.py`: `title` and `tags` both have a validator that trims and rejects whitespace-only values; `assignee` had no validator at all, so `"   "` was stored as-is instead of being treated as "unassigned" | **Useful** | Real, reproducible inconsistency — confirmed empirically (`TaskCreate(title="X", assignee="   ").assignee` returned `'   '`, not `None`). Fixed with a matching `_clean_assignee` validator. |
| 3 | "The overdue filter in `list_tasks` (`t.due_date < today`) has a timezone bug — comparing dates across timezones can give the wrong result" | **Wrong** | Factually incorrect for this codebase: `due_date` is a Pydantic `date` (not `datetime`), and `date.today()` returns a `date` — neither carries a time or timezone component, so there's nothing for a timezone bug to attach to. This exact question was already reasoned through in `docs/midcourse/mini-adr.md` ADR-01. A generic reviewer pattern-matching "date comparison" to "probably a timezone bug" without checking the actual types involved would be wrong here. |

---

## AI Security Review — Graded Findings

| # | Finding | Grade | Reasoning |
|---|---|---|---|
| 1 | Stored XSS via the `tags` field: an unescaped tag string like `<img src=x onerror=alert(1)>` (28 chars, under the 30-char tag limit) gets injected directly into card HTML | **Valid** | Confirmed exploitable: created a task with that exact tag, loaded the board in a browser, and inspected the DOM — before the fix, the payload would execute as real HTML. Fixed by routing tags through `esc()` like every other field. Manually re-verified after the fix (see "Manual Check" below). |
| 2 | `description` has no `max_length` (unlike `title`'s 200 and `assignee`'s 100), so a client can send an arbitrarily large string | **Valid** (low severity) | Confirmed: `TaskCreate(title="X", description="x"*100000)` is accepted without error. Real gap, but low severity for this project's actual deployment (single-process in-memory store, no auth, local/course use — not a public production service). Documented here rather than fixed, since adding a length limit is a product/UX decision (what's a reasonable max?) rather than an unambiguous bug fix, and is out of scope for a "small fix" on this branch. |
| 3 | "CORS `allow_methods=["*"]` and `allow_headers=["*"]` is a security risk — should be restricted to specific methods/headers" | **False Positive** | The origin allow-list (`app/main.py`) is the actual security boundary here, and it's already scoped (ADR-07). There is no authentication, no cookies, and no credentialed requests anywhere in this app, so there's no session or credential for a cross-origin request to steal via a permissive method/header policy — the classic risk this kind of finding is meant to catch doesn't apply. Restricting methods/headers further would add complexity without closing any real gap. |

---

## Manual Check

Reproduced and re-verified the XSS fix by hand rather than trusting the code diff alone:
1. Started an isolated instance of the app (backend on `:8000`, frontend on `:9500`).
2. `POST /tasks` with `tags: ["<img src=x onerror=alert(1)>"]` → `201`, tag stored as sent (correct — escaping is a render-time concern, not an input-validation one).
3. Loaded the board in a real browser and inspected the rendered DOM directly via JS: `tagEl.innerHTML` showed `&lt;img src=x onerror=alert(1)&gt;` (escaped), `document.querySelectorAll('.card img').length` was `0` (no `<img>` element was actually created), and no console errors/alerts fired.
4. Deleted the test task afterward.

---

## One Rejected AI Suggestion

While reviewing `app/main.py`, I considered proposing that `POST /tasks` should reject any `status` other than `ToDo` — right now a client can create a task directly as `Done`, completely bypassing the `ToDo→InProgress→Done` transition state machine (confirmed: `POST /tasks {"title":"X","status":"Done"}` succeeds with `201`).

**I rejected this suggestion** for three reasons:
1. It's not required by the spec — the official Module 2 `verify_a.py` script checks that `status` *defaults* to `ToDo`, but never asserts that other values are rejected at creation.
2. There's a legitimate real-world case for it: importing already-completed tasks or seeding test data shouldn't require replaying a full transition sequence.
3. Implementing it now would be a behavior change to existing, working functionality — exactly the kind of thing `AGENTS.md` says to avoid on this branch ("if you're unsure whether a change counts as a new feature vs. a small fix, treat it as a feature and don't make it without asking first").

Left as-is; noted here rather than silently dropped, in case a future project phase wants to revisit it as an actual feature decision.

---

## Ownership Statement

Every line of code in this repository — backend, frontend, tests, and documentation — was written by Claude (Anthropic) under my direction, following the course's plan-implement-verify workflow. I did not write the implementation myself, but I read every diff before accepting it, ran the test suite and the app after each change, and made the actual decisions about scope, priority, and trade-offs (e.g., rejecting the "restrict creation status" suggestion above, choosing not to fix the unbounded `description` field, deciding what belonged in this branch versus what would count as a forbidden new feature). The two real bugs in this review (the tags XSS and the assignee whitespace gap) were things I asked the AI to find, not things it volunteered — the review only happened because I directed it to happen. I own the correctness and scope decisions in this codebase, even though I did not type the code.
