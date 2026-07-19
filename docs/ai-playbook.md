# My Personal AI Playbook

*One page. Written after building Task Tracker end-to-end with AI doing the typing and me doing the deciding.*

## When I reach for AI / when I don't
I ask AI to write all code, tests, and docs — I don't type them myself. I ask it to reproduce a bug before explaining it, and to find and quote a primary source rather than trust my memory of course material. I don't ask AI whether my own decision is "good enough" as a stand-in for making the decision, and I don't accept "it should work" as verification — if it can't show me a passing test or a real request/response, nothing's been verified.

## Never-paste rule
I never paste real secrets, API keys, tokens, `.env` contents, credentials, or real personal data (names beyond my own, emails, phone numbers, production logs) into a prompt or into this repo — test/demo data only. `.gitignore` blocks `.env*` for the same reason; `docs/release-evidence.md` includes a secrets scan before every submission.

## Review rules
1. Every diff gets read before it's accepted — not skimmed.
2. Claims get checked against reality, not against how confident they sound — `verify_a.py` failing on this project's first run is why I trust "run it" over "read about it."
3. Every AI review comment gets graded Useful / Noise / Wrong honestly (see `docs/final-ai-review.md`) — not everything flagged is real, and not everything real gets flagged the first time. The explicit-null bug in that file was caught by instructor review, not mine — logged, not hidden.
4. Anywhere AI writes state-machine logic, I now ask: "what happens if the input equals the current state, or a required field is sent null?" — both caused real regressions here.

## Verification rules
- Reproduce before explaining: curl the endpoint, load the page, read the actual response/DOM.
- A green suite isn't the finish line if it doesn't cover what broke — 63/63 passing didn't stop two real bugs from shipping in earlier commits.
- When AI and I disagree on scope, the assignment brief wins, not either of our assumptions.

## Ownership rules
I decide what ships; AI proposes, and I write down what I accepted, edited, or rejected (`docs/final-ai-review.md`, `docs/midcourse/prompt-log.md`). Instructor feedback is a review pass like any other — I reproduce it, fix it, and log it, same as a self-found bug. Not catching something myself doesn't reduce my ownership of the result.

## Decision Card
- **Decision:** Do the full Module 2 compliance rebuild (priority, assignee, PATCH, 422) before the end-of-course project started.
- **Context:** Neither brief required it; my own earlier notes once described the non-compliant version as if it were the spec.
- **AI's role:** Found the gap via `verify_a.py`, implemented the fix across model/backend/frontend/tests.
- **My verification:** Ran `verify_a.py` and the full suite before/after, tested live in a browser, cross-checked three independent course sources first.
- **Outcome:** Fixed — correct call; closing a confirmed gap before a scope-restricted branch exists costs nothing.

**Commitment:** I'll re-read this page in 30 days and cross out anything that turned out to be wrong.
