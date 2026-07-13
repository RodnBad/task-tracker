# User Stories — Mid-Course Project

## Feature A: Due Dates + Overdue Filter

**US-A1 — Set a due date when creating a task**
> As a user, I want to assign a due date to a task when I create it, so that I can track when it needs to be completed.
- Acceptance: POST /tasks accepts `due_date` (ISO date, optional). The field is returned in the response.

**US-A2 — Edit the due date of an existing task**
> As a user, I want to change or remove the due date of an existing task, so that I can adjust schedules as plans change.
- Acceptance: PUT /tasks/{id} with `due_date` updates the field. Setting to `null` clears it.

**US-A3 — Filter overdue tasks**
> As a user, I want to see only tasks that are past their due date and not yet done, so that I can prioritise what is urgent.
- Acceptance: GET /tasks?overdue=true returns tasks where `due_date < today` and `status != done`.

**US-A4 — See overdue tasks highlighted in the Kanban board**
> As a user, I want overdue tasks to be visually highlighted on the board, so that I notice them at a glance.
- Acceptance: Cards with an overdue due date show a red left border and an "⚠ overdue" label.

**AI assumption corrected:** The AI's first draft of the overdue filter (Prompt A2) treated "overdue" loosely and didn't specify whether a task due *today* counts as overdue. Left as written it would have been ambiguous at the boundary. I explicitly constrained the rule to `due_date < today` (strictly before today, not `<=`), so a task due today is not flagged overdue until tomorrow — matching the acceptance criteria above.

---

## Feature B: Tags / Labels

**US-B1 — Add tags to a task**
> As a user, I want to label tasks with one or more tags (e.g., "bug", "frontend"), so that I can categorise my work.
- Acceptance: POST /tasks accepts `tags` (list of strings, default empty). Tags are returned in the response.

**US-B2 — Edit tags on an existing task**
> As a user, I want to update or clear the tags on a task, so that I can re-categorise it as the project evolves.
- Acceptance: PUT /tasks/{id} with `tags` replaces the tag list. An empty list clears all tags.

**US-B3 — Filter tasks by tag**
> As a user, I want to filter tasks by a specific tag, so that I can focus on a particular category of work.
- Acceptance: GET /tasks?tag=<label> returns only tasks whose `tags` list contains that label.

**US-B4 — Combine tag and overdue filters**
> As a user, I want to combine the tag filter with the overdue filter, so that I can find overdue tasks in a specific category.
- Acceptance: GET /tasks?overdue=true&tag=bug returns tasks that are both overdue and tagged "bug".

**AI assumption corrected:** The AI's initial `tags: list[str]` field (Prompt B1) had no validation — it would silently accept empty strings, whitespace-only tags, and an unbounded number of tags. That's not what "tag" implies for a category label. I corrected this by adding a `field_validator` (see ADR-05) that trims whitespace, rejects empty/whitespace-only tags with a 422, and caps tags at 10 per task / 30 characters each.
