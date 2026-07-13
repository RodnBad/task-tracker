# Prompt Log — Mid-Course Project

This log documents the AI-assisted workflow used to build Features A and B.

---

## Feature A: Due Dates + Overdue Filter

### Prompt A1 — Data model extension
**Tool:** Claude (browser)
**Prompt:**
> i have a pydantic v2 Task model, fields are id, title, description, status (enum). want to add a due date to it, optional, just a plain date not datetime, no timezone stuff. use python's date. just show me the field, not the whole file

**AI output summary:**
Suggested `due_date: Optional[date] = None` with `from datetime import date`. Correctly used `Optional` and defaulted to `None`. No changes to existing fields.

**What I kept:** The field definition exactly as suggested.

---

### Prompt A2 — Overdue filter endpoint
**Tool:** Claude (browser)
**Prompt:**
> ok now on GET /tasks i want an optional query param overdue (bool). when true, only return tasks where due_date is before today AND status isn't done. just give me the updated function signature + the filter part, don't need the whole file again

**AI output summary:**
Suggested using `Query(default=None)`, `date.today()` for comparison, and a list comprehension filter. Correctly excluded done tasks.

**What I kept:** The filter logic as suggested. Added the `from datetime import date` import myself since AI omitted it — server crashed with a `NameError` on first run, caught it there.

---

### Prompt A3 — Frontend overdue highlight
**Tool:** Claude (browser)
**Prompt:**
> in my kanban board (vanilla js) i render cards for each task. each task has due_date (string YYYY-MM-DD or null) and status. write me a snippet that checks if a card is overdue (due_date < today, status not done), adds a class "overdue" to the card div, and shows a badge that goes red when it's overdue

**AI output summary:**
Suggested comparing `task.due_date < today` where `today = new Date().toISOString().split('T')[0]`. Worked correctly because ISO strings compare lexicographically.

**What I kept:** The comparison logic and badge HTML. Changed the CSS to a red left-border instead of a solid red background, looked too aggressive on the board.

---

### Prompt A4 — Invalid date format test
**Tool:** Claude (browser)
**Prompt:**
> write a pytest that checks POST /tasks with due_date "not-a-date" gives 422, and same thing for PUT with something like "31-12-2026". don't write any new validation code for this, pydantic should already reject bad dates on its own, i just never actually wrote a test proving it

**AI output summary:** Generated both tests directly against the existing `date` field, no new backend code needed. Confirmed Pydantic v2 rejects non-ISO date strings automatically.

**What I kept:** Both tests as-is — this closed a gap where the behavior was already correct but nothing actually proved it.

---

## Feature B: Tags / Labels

### Prompt B1 — Tags field in model
**Tool:** Claude (browser)
**Prompt:**
> add a tags field to the Task model, pydantic v2. list of strings, default empty list, use Field(default_factory=list). also add it to TaskCreate and TaskUpdate (optional on update). just the field additions pls

**AI output summary:**
Correctly used `list[str]` with `Field(default_factory=list)` for Task and TaskCreate, and `Optional[list[str]] = None` for TaskUpdate. No issues.

**What I kept:** All suggestions as-is.

---

### Prompt B2 — Tag filter endpoint
**Tool:** Claude (browser)
**Prompt:**
> same GET /tasks, add another optional query param tag (string). if it's given, only return tasks where that string is in their tags list. exact match is fine for now. just the filter addition

**AI output summary:**
Suggested `tasks = [t for t in tasks if tag in t.tags]`. Simple and correct.

**What I kept:** Exactly as suggested. Combined with the overdue filter using sequential list comprehensions so both filters can be applied at once.

---

### Prompt B3 — Frontend tag display and filter
**Tool:** Claude (browser)
**Prompt:**
> on the kanban cards, show tags as little colored pill/badge things. also want a text box in the header where i type a tag and it filters the visible cards — do this client side, no need to hit the api again. give me the pill html and the js filter

**AI output summary:**
Suggested `<span class="tag">` pills and a filter using `.some(g => g.toLowerCase().includes(filterValue))`. The `includes` approach allows partial tag matching (e.g., "front" matches "frontend").

**What I kept:** The pill HTML and the JS filter. Kept the partial matching, felt better than requiring the exact tag spelling.

---

### Prompt B4 — Combined filter test
**Tool:** Claude (browser)
**Prompt:**
> write a pytest for the combined overdue=true&tag=bug filter. make 3 tasks — one matches both, one is overdue but wrong tag, one has the right tag but isn't overdue. assert only the first one comes back

**AI output summary:**
Generated a clean test with clear task setup. Used `date.today() - timedelta(days=1)` for overdue.

**What I kept:** The test structure. Renamed a couple variables so they read clearer.

---

### Prompt B5 — Tag validation (weak prompt rewritten into a strong prompt)

**Weak prompt (first attempt):**
> add validation for tags

**Why it was weak:** didn't say which model, which field, or what "validation" even means here. AI could've done literally anything — a regex check, a length limit, nothing useful. too vague to trust the output without a ton of back and forth.

**Strong prompt (rewritten):**
**Tool:** Claude (browser)
> ok being more specific — i have tags: list[str] on TaskCreate and TaskUpdate (pydantic v2, optional on update). want a field_validator that: strips whitespace off each tag, errors out if a tag is empty after stripping, rejects if there's more than 10 tags, rejects any single tag over 30 chars. just give me the validator function + the import i need

**AI output summary:** Produced a `@field_validator("tags")` classmethod covering all four rules, raising `ValueError` inside the validator (FastAPI turns this into a 422 automatically). Applied it to `TaskCreate` only in the first pass.

**What I kept:** The validation logic as-is. I pulled the per-tag cleaning out into a shared `_clean_tags()` helper and wired the same validator onto `TaskUpdate.tags` myself (as `Optional[list[str]]`, skipped when the field's unset) — the AI's version only covered `TaskCreate`, would've let updates bypass the rules entirely.

---

### Prompt B6 — Missing edge-case tests
**Tool:** Claude (browser)
**Prompt:**
> write pytests for that tag validator: reject an empty string tag on create, reject a whitespace-only tag, check tags actually get trimmed, reject more than 10 tags, reject an empty tag on a PUT update too. also check tags don't get wiped out when i update something unrelated like the title

**AI output summary:** Generated all six tests with clear naming. Used a list comprehension (`[f"tag{i}" for i in range(11)]`) to build the too-many-tags payload.

**What I kept:** All six tests as generated, renamed one (`test_reject_empty_tag_on_update`) to match the naming pattern already used in the rest of the file.
