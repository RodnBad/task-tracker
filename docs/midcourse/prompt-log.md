# Prompt Log — Mid-Course Project

This log documents the AI-assisted workflow used to build Features A and B.

---

## Feature A: Due Dates + Overdue Filter

### Prompt A1 — Data model extension
**Tool:** Claude (browser)
**Prompt:**
> I have a Pydantic v2 Task model with fields: id, title, description, status (TaskStatus enum). I want to add an optional due date field. The date should be a plain date (no time, no timezone). Use Python's datetime.date. Show only the updated model fields, not the full file.

**AI output summary:**
Suggested `due_date: Optional[date] = None` with `from datetime import date`. Correctly used `Optional` and defaulted to `None`. No changes to existing fields.

**What I kept:** The field definition exactly as suggested.

---

### Prompt A2 — Overdue filter endpoint
**Tool:** Claude (browser)
**Prompt:**
> I have a FastAPI GET /tasks endpoint that returns all tasks. Add an optional query parameter `overdue: Optional[bool]` that, when true, filters to tasks where due_date is before today and status is not "done". Show only the updated function signature and filter logic, not the full file.

**AI output summary:**
Suggested using `Query(default=None)`, `date.today()` for comparison, and a list comprehension filter. Correctly excluded done tasks.

**What I kept:** The filter logic as suggested. Added the `from datetime import date` import myself since AI omitted it.

---

### Prompt A3 — Frontend overdue highlight
**Tool:** Claude (browser)
**Prompt:**
> In my Kanban board (vanilla JS), I render task cards. Each task has a `due_date` (string, YYYY-MM-DD or null) and `status`. Write a JS snippet that: (1) determines if a card is overdue (due_date < today, status != "done"), (2) adds a CSS class "overdue" to the card div, (3) shows a due date badge that turns red when overdue.

**AI output summary:**
Suggested comparing `task.due_date < today` where `today = new Date().toISOString().split('T')[0]`. Worked correctly because ISO strings compare lexicographically.

**What I kept:** The comparison logic and badge HTML. Adjusted CSS to use `border-left` instead of background color for subtlety.

---

### Prompt A4 — Invalid date format test
**Tool:** Claude (browser)
**Prompt:**
> Write a pytest test confirming that POST /tasks with `due_date: "not-a-date"` returns 422, and another confirming PUT /tasks/{id} with a malformed date string (e.g. "31-12-2026") also returns 422. Don't add any new validation code — Pydantic's `date` type should already reject these.

**AI output summary:** Generated both tests directly against the existing `date` field, no new backend code. Confirmed Pydantic v2 rejects non-ISO date strings automatically.

**What I kept:** Both tests as-is — this closed a gap where the behavior was already correct but untested.

---

## Feature B: Tags / Labels

### Prompt B1 — Tags field in model
**Tool:** Claude (browser)
**Prompt:**
> Add a `tags` field to my Pydantic v2 Task model. Tags are a list of strings, default to an empty list. Use `Field(default_factory=list)`. Also add it to TaskCreate and TaskUpdate (optional on update). Show only the field additions.

**AI output summary:**
Correctly used `list[str]` with `Field(default_factory=list)` for Task and TaskCreate, and `Optional[list[str]] = None` for TaskUpdate. No issues.

**What I kept:** All suggestions as-is.

---

### Prompt B2 — Tag filter endpoint
**Tool:** Claude (browser)
**Prompt:**
> Extend my GET /tasks endpoint to accept an optional query parameter `tag: Optional[str]`. When provided, filter tasks to only those whose `tags` list contains that exact string. Show only the filter logic addition.

**AI output summary:**
Suggested `tasks = [t for t in tasks if tag in t.tags]`. Simple and correct.

**What I kept:** Exactly as suggested. Combined with the overdue filter using sequential list comprehensions.

---

### Prompt B3 — Frontend tag display and filter
**Tool:** Claude (browser)
**Prompt:**
> In my Kanban frontend, each task card should show its tags as coloured pill badges. Also add a text input in the header that filters visible cards by tag (client-side, not a new API call). Show the HTML for a tag pill and the JS filter logic.

**AI output summary:**
Suggested `<span class="tag">` pills and a filter using `.some(g => g.toLowerCase().includes(filterValue))`. The `includes` approach allows partial tag matching (e.g., "front" matches "frontend").

**What I kept:** The pill HTML and the JS filter. Chose to keep partial matching for better UX.

---

### Prompt B4 — Combined filter test
**Tool:** Claude (browser)
**Prompt:**
> Write a pytest test that verifies the combined `?overdue=true&tag=bug` filter. Create 3 tasks: one that matches both conditions, one that is overdue but has a different tag, one that has the right tag but is not overdue. Assert only 1 task is returned.

**AI output summary:**
Generated a clean parametrised test with clear task setup. Used `date.today() - timedelta(days=1)` for overdue.

**What I kept:** The test structure. Renamed variables for clarity.

---

### Prompt B5 — Tag validation (weak prompt rewritten into a strong prompt)

**Weak prompt (first attempt):**
> Add validation for tags.

**Why it was weak:** No model name, no field name, no rules. The AI would have to guess what "validation" means here — it could have added a generic non-null check, a regex, or nothing useful at all. Too vague to review confidently.

**Strong prompt (rewritten):**
**Tool:** Claude (browser)
> I have a Pydantic v2 `tags: list[str]` field on `TaskCreate` and `TaskUpdate` (optional on update). Add a `field_validator` that: (1) strips whitespace from each tag, (2) raises a validation error if any tag is empty after stripping, (3) rejects the payload if there are more than 10 tags, (4) rejects any tag longer than 30 characters. Show only the validator function and the necessary import.

**AI output summary:** Produced a `@field_validator("tags")` classmethod covering all four rules, raising `ValueError` inside the validator (FastAPI turns this into a 422 automatically). Applied it to `TaskCreate` only in the first pass.

**What I kept:** The validation logic as-is. I extracted the per-tag cleaning into a shared `_clean_tags()` helper and applied the same validator to `TaskUpdate.tags` (as `Optional[list[str]]`, skipping validation when the field is unset) since the AI's first pass only covered `TaskCreate`.

---

### Prompt B6 — Missing edge-case tests
**Tool:** Claude (browser)
**Prompt:**
> Write pytest tests for the tag validator above: reject an empty-string tag on create, reject a whitespace-only tag, confirm tags are trimmed of surrounding whitespace, reject more than 10 tags, and reject an empty tag on a PUT update. Also confirm tags are unchanged when an unrelated field (title) is updated.

**AI output summary:** Generated all six tests with clear naming. Used a list comprehension (`[f"tag{i}" for i in range(11)]`) to build the too-many-tags payload.

**What I kept:** All six tests as generated, renamed one (`test_reject_empty_tag_on_update`) for consistency with the rest of the file's naming convention.
