# Final AI Review — End-of-Course Project

AI code review and security review of the codebase, done on the `final-project` branch, with every finding graded honestly rather than accepted at face value — per `AGENTS.md`'s review expectations.

---

## AGENTS.md Guardrails Confirmed

Every `app/`/`frontend/` change made on this branch, in full (this list was previously incomplete — corrected after instructor feedback flagged the inconsistency):

| Change | File(s) | Category | Why it's in scope |
|---|---|---|---|
| Stored XSS fix — tags weren't `esc()`-escaped in card rendering | `frontend/index.html` | Security fix | One-line escaping fix to an existing render path — no new field, no new UI, no new behavior for a legitimate user. |
| `assignee` whitespace-only not normalized/validated | `app/models.py` | Bug fix | Brings `assignee` in line with how `title`/`tags` already behave — a consistency/correctness fix, not new functionality. |
| `GET /health` endpoint added | `app/main.py` | Release-readiness infra | Required by Part B for the Docker `HEALTHCHECK`; a monitoring endpoint, not a product feature — doesn't change any existing behavior. |
| Explicit `null` on required fields (`status`, `title`, `description`, `priority`, `tags`) was silently accepted via `PATCH`, corrupting the task and bypassing transition validation | `app/models.py` | Bug fix (data-integrity / security) | Found via instructor review of this submission. Confirmed exploitable (`PATCH {"status": null}` returned `200` and set status to `null`, matching no Kanban column). Fixed with a `model_validator` that rejects explicit null on required fields while still allowing it on the genuinely-nullable `assignee`/`due_date`. See the Security Review table below. |

Everything else added on this branch (`AGENTS.md`, `docs/release-evidence.md`, this file, `docs/ai-playbook.md`, the Dockerfile `HEALTHCHECK`, the `.dockerignore` additions, the CI `docker` job) is documentation or CI/Docker configuration — not `app/`/`frontend/` code, and not a product feature.

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
| 4 | `PATCH /tasks/{id}` accepted an explicit `null` for required fields (`status`, `title`, `description`, `priority`, `tags`) and applied it, corrupting the task and — for `status` specifically — bypassing transition validation entirely (`if payload.status is not None` was `False`, so `assert_valid_transition` never ran) | **Valid** — the one I missed on the first review pass | Not caught in my original review; caught by the instructor's review of this submission instead. Reproduced first (`PATCH {"status": null}` → `200`, task's status became `null`, matching no Kanban column), then fixed with a `model_validator(mode="after")` on `TaskUpdate` that inspects `model_fields_set` to distinguish "field omitted" from "field explicitly sent as null" — a `field_validator` alone can't tell those apart. `assignee`/`due_date` deliberately excluded since `null` is their correct way to clear a value. 7 new regression tests added (one per required field, plus two confirming `assignee`/`due_date` still accept null). |
| 5 | A title/assignee/tag made up entirely of zero-width Unicode characters (e.g. U+200B ZERO WIDTH SPACE) survives `str.strip()` — which only removes characters where `.isspace()` is `True`, and these aren't — so it reads as "blank" to a human but passes the existing empty/whitespace-only checks | **Valid** | Found by an independent adversarial review pass (below), not by me. Confirmed: `POST /tasks {"title": "​"}` → `201` before the fix (an invisible task title). Same root cause hit `assignee` and `tags` too — notably the *exact same class of bug* as finding #4 above, just a Unicode edge case of it rather than a new category. Fixed with a shared `_strip_invisible()` helper (`app/models.py`) applied to all three fields; 2 new regression tests (reject invisible-only content, and confirm legitimate content with a stray invisible character gets cleaned rather than rejected). |

---

## Adversarial Review (Independent Pass)

After fixing finding #4, I asked a fresh reviewer — with no memory of writing this code, briefed only on the bug history above — to actively try to break the app rather than confirm my fixes worked. Full findings:

**Found and fixed:** #5 above (zero-width-character bypass on title/assignee/tags).

**Found and consciously left as-is** (not corruption, not security-severity, genuinely a design question rather than a bug):
- Duplicate tags are allowed (`["dup","dup"]` → both stored). No dedup logic exists, and it isn't documented either way. Not fixing on this branch — deduping would be a behavior change, not an unambiguous bug fix, and nothing requires it.
- The tag filter is exact-match/case-sensitive on the backend (`GET /tasks?tag=`) but substring/case-insensitive on the frontend's client-side filter box. Both are internally consistent and already tested; this is a UX/API asymmetry, not a defect in either one.

**Hypotheses tested and disproven** (real effort was spent trying to break these; they held up):
- `TaskCreate` doesn't need the null-rejection validator at all — none of its fields are `Optional`, so Pydantic's own type system rejects `null` before any custom validator runs. Confirmed for every required field.
- `extra="forbid"` combined with an explicit-null required field in the same request (e.g. `{"status": null, "made_up": "x"}`) still fails cleanly (422) with the task provably untouched, regardless of which error triggers first.
- Two nulled required fields in one request produce a single combined error, not a partial application of one and rejection of the other.
- A request mixing a valid status transition with a genuine null-clear (e.g. `{"status": "InProgress", "assignee": null}`) applies both correctly — no interference between the new validator and legitimate nullable fields.
- Extensive malformed-input fuzzing (wrong types for every field, invalid calendar dates, non-dict JSON bodies, bad query params) never produced a `500` — every case returned a clean `4xx`.
- Every other frontend render site was traced for unescaped injection beyond the already-fixed `tags` field; the remaining unescaped values (`due_date`, `priority`, `id`) are all constrained by Pydantic types or server-generated, so none are attacker-reachable.

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

Every line of code in this repository — backend, frontend, tests, and documentation — was written by Claude (Anthropic) under my direction, following the course's plan-implement-verify workflow. I did not write the implementation myself, but I read every diff before accepting it, ran the test suite and the app after each change, and made the actual decisions about scope, priority, and trade-offs (e.g., rejecting the "restrict creation status" suggestion above, choosing not to fix the unbounded `description` field, deciding what belonged in this branch versus what would count as a forbidden new feature). The two real bugs in this review (the tags XSS and the assignee whitespace gap) were things I asked the AI to find, not things it volunteered — the review only happened because I directed it to happen. The explicit-null bug was not one I caught — the instructor's review of this submission found it, and I own that miss as much as I own the catches: my first review pass wasn't thorough enough on `TaskUpdate`'s required-field handling, and I've since reproduced, fixed, and regression-tested it rather than taking the report at face value. After fixing it, I explicitly asked for an independent adversarial pass rather than declaring the fix done on my own say-so — that's how the zero-width-character variant of the same bug class (finding #5) got caught before a second instructor review would have had to find it for me. I own the correctness and scope decisions in this codebase, even though I did not type the code.
