# My Personal AI Playbook

*(One page. Written after building Task Tracker end-to-end with AI doing the typing and me doing the deciding.)*

## When I reach for AI
- Any time I need working code, tests, or docs written — I ask, I don't type it myself. Speed isn't the point; it's that reviewing is a better use of my attention than drafting.
- When I'm not sure a piece of course material is actually authoritative (a summary, a chat transcript, a stale note) — I ask AI to go find and quote the primary source rather than trust my memory of it.
- When something *feels* wrong in the running app (a status change that silently failed, a field that looked off) — I ask AI to reproduce it first, not explain it first.

## When I don't
- I don't ask AI whether my own decision is "good enough" as a substitute for making the decision. When the transition-rule fix conflicted with the end-of-course project's "no new features" rule, that was my call to make, not something to defer.
- I don't accept "it should work" as verification. If AI can't show me a passing test or a real request/response, it hasn't verified anything.

## Non-negotiables
1. **Every diff gets read before it gets accepted.** Not skimmed — read.
2. **Claims get checked against reality**, not against how confident the explanation sounds. The `verify_a.py` script failing with `ImportError` on the very first run of this project is the reason I trust "run it" over "read about it."
3. **A green test suite is not the finish line if the tests don't cover the thing that broke.** The tags-XSS bug and the assignee-whitespace bug both passed 54/54 tests right up until I specifically went looking for them.
4. **Same-status validation and status casing are the source of two separate regressions in this project** (`in_progress→todo` misclassified as valid, then a frontend bug that resent the unchanged status on every edit) — anywhere AI writes state-machine logic, I now explicitly ask "what happens when the input equals the current state?" before moving on.

## Review rules
- Grade every AI-generated review comment honestly: Useful, Noise, or Wrong — not everything AI flags is real, and not everything real gets flagged (see `docs/final-ai-review.md` for the "Wrong" and "False Positive" examples from this exact project).
- Prefer a manual reproduction (curl the endpoint, load the actual page, read the actual DOM) over trusting a written explanation of what "should" happen.
- When AI and I disagree on scope, the actual assignment brief wins — not my assumption, not AI's suggestion. I was wrong about `PUT`/`400` being fine until I checked; AI was wrong about "restrict creation to ToDo-only" being in scope until I checked the brief.

## Open questions I'm carrying forward
- How much of "trust but verify" scales once the codebase is too large for me to read every diff line-by-line? This project stayed reviewable because it's small.
- When course materials genuinely disagree with each other (the `verify_a.py` gap a classmate flagged in the Week 1 session), whose correction should win by default — mine, the AI's, or the instructor's — before I actually ask?

## Decision Card
- **Decision:** Whether to do the full Module 2 compliance rebuild (priority, assignee, PATCH, 422) before the end-of-course project started.
- **Context:** Neither the mid-course nor end-of-course brief required it; my own earlier notes showed I once thought the non-compliant version *was* the spec.
- **AI's role:** Found the gap via `verify_a.py`, proposed the full fix, implemented it across model/backend/frontend/tests.
- **My verification:** Ran `verify_a.py` before/after, ran the full suite, tested live in a browser, cross-checked three separate course sources (lecture notes, quiz key, live-session transcript) before deciding it was a real gap and not a design choice.
- **Outcome:** Fixed. Correct call — closing a confirmed gap costs nothing when done before the branch with restricted scope exists.

**Commitment:** I'll re-read this page in 30 days and cross out anything that turned out to be wrong.
