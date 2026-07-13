# Reflection — Mid-Course Project

## What worked well

**Incremental prompting.** Asking the AI for one small addition at a time (one field, one filter, one test) kept each output short and easy to review. When I asked for "the full updated file," the AI would sometimes restructure things unnecessarily. Smaller prompts produced cleaner diffs.

**Using the model as a first draft, not a final answer.** For the overdue filter, the AI suggested comparing ISO date strings directly (`due_date < today`). I verified that Python's `datetime.date` comparison is the right approach (not string comparison), and replaced the AI's string approach in the test fixtures with proper `date.today() - timedelta(days=1)`. The frontend still uses string comparison, which works correctly because ISO strings sort lexicographically — but I confirmed this before accepting it.

**Break tests first.** Writing tests that tried invalid operations (overdue filter returning done tasks, tag filter returning no match) before writing the happy-path tests helped clarify exactly what the feature needed to do. The AI-suggested tests tended to be happy-path only; I added the edge cases myself.

**Pydantic v2 handled the new fields cleanly.** Adding `due_date` and `tags` to the model required no changes to `storage.py` — the in-memory store just stores whatever the model contains. This validated the decision to keep storage generic.

---

## What didn't work well

**The AI sometimes added imports it forgot to include.** In Prompt A2, the AI's filter logic used `date.today()` but didn't include `from datetime import date` in the snippet. I caught this when running the server and got a `NameError`. Lesson: always check imports when the AI gives you a partial snippet.

**Frontend filter interaction wasn't fully thought through by the AI.** When I asked for a tag filter in the header, the AI gave me a separate fetch to `/tasks?tag=<label>` instead of client-side filtering. This would lose any overdue filter state. I changed it to pure client-side filtering (filtering `allTasks` in memory) so both filters work together without resetting each other.

**Test isolation needed an autouse fixture.** My first test run had state leaking between tests because the in-memory store wasn't being cleared. The AI suggested using `@pytest.fixture(autouse=True)` in conftest.py to call `storage.clear()` before each test — this worked well once I understood why it was needed.

---

## What I'd do differently

- **Start with the test file, not the implementation.** Writing the tests first made the expected API contract explicit before touching `models.py` or `main.py`. I'd do this from the start next time rather than retrofitting tests.
- **Ask the AI to explain its reasoning, not just generate code.** For the date comparison approach, asking "why is ISO string comparison safe here?" would have given me confidence faster than manually verifying it.
- **Use CLAUDE.md from day one.** I added the CLAUDE.md at the end. Starting with it would have kept the AI's context more consistent across prompts.
