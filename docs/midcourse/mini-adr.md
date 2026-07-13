# Architecture Decision Record — Mid-Course Project

## ADR-01: Store due_date as an ISO date string (not datetime)

**Context:** Tasks need an optional deadline. The question was whether to store a full datetime (with time + timezone) or a plain date.

**Options considered:**
1. `datetime` with timezone — precise, but overkill for a daily deadline
2. `date` (YYYY-MM-DD) — simple, unambiguous, no timezone complexity
3. Unix timestamp integer — hard to read, no benefit here

**Decision:** Use `datetime.date` via Pydantic (`Optional[date]`), serialised as `YYYY-MM-DD`.

**Consequences:** Overdue comparison is `due_date < date.today()` — simple and timezone-safe because both sides are plain dates. No timezone edge cases to handle.

---

## ADR-02: Store tags as a plain list of strings (no tag entity)

**Context:** Tasks need categorisation labels. Options ranged from a separate Tag model with IDs to a simple string list.

**Options considered:**
1. Separate `Tag` model with its own CRUD endpoints — normalised, allows tag management
2. `list[str]` on the Task model — denormalised, no separate entity needed
3. Single comma-separated string — harder to query, error-prone

**Decision:** `tags: list[str]` on the `Task` model.

**Consequences:** Simple to implement and test. Tag filtering is a single `in` check. Downside: no central tag registry, so typos create duplicate tags — acceptable for this scope.

---

## ADR-03: Implement filters as query parameters on GET /tasks (not new endpoints)

**Context:** Both features require filtering. Options were new endpoints vs. query parameters on the existing list endpoint.

**Options considered:**
1. New endpoints — `GET /tasks/overdue`, `GET /tasks/by-tag/{tag}` — clean URLs but multiplies endpoints
2. Query parameters on `GET /tasks` — one endpoint, combinable filters

**Decision:** Query parameters (`?overdue=true`, `?tag=<label>`) on the existing `GET /tasks` endpoint.

**Consequences:** Filters are trivially composable (`?overdue=true&tag=bug`). No new routes, no changes to the frontend's base fetch URL. Follows REST conventions for filtering collections.

---

## ADR-04: Keep in-memory storage (no database)

**Context:** Course constraint. The mid-course project explicitly states to use in-memory storage.

**Decision:** Maintain the existing `storage.py` dict-based store. The new fields (`due_date`, `tags`) are simply added to the `Task` Pydantic model — the storage layer requires no changes.

**Consequences:** Data is lost on restart. Acceptable for the course project. The storage interface (`save`, `get_all`, `get_by_id`, `delete`) is clean enough to swap for a real DB later.

---

## ADR-05: Validate tags with a Pydantic field_validator (trim, non-empty, capped)

**Context:** The initial `tags: list[str]` field had no validation — empty strings, whitespace-only tags, and unbounded tag counts were all silently accepted. The spec calls for "trimmed non-empty tag values and optional maximum count/length."

**Options considered:**
1. No validation — simplest, but allows junk data (`""`, `"   "`) to reach storage and the UI.
2. Validate in the route handler — works, but duplicates logic between create and update and bypasses FastAPI's automatic 422 response.
3. Pydantic `field_validator` on `TaskCreate.tags` and `TaskUpdate.tags` — validation runs at the model boundary, FastAPI converts `ValueError` to a 422 automatically, and both create/update reuse one helper.

**Decision:** Option 3. Added a shared `_clean_tags()` helper in `models.py`, wired into both `TaskCreate` and `TaskUpdate` via `@field_validator("tags")`. Tags are stripped of surrounding whitespace, rejected if empty after stripping, capped at 10 tags per task, and capped at 30 characters per tag.

**Consequences:** `POST /tasks` and `PUT /tasks/{id}` now return 422 for `["", "  "]`-style tags instead of silently storing them. The 10/30 limits are arbitrary but reasonable for a label field — documented here so they're easy to revisit if a real use case needs more.
