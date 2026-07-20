# My Personal AI Playbook

## When I reach for AI first
Any task producing code, tests, or docs — every line of this repo. Also for grounding: instead of trusting my memory of a requirement, I ask AI to find and quote the actual source PDF. That's how the real `TaskPriority` gap and the Decision Card's real format both got found — my first draft of each was a guess, not a lookup.

## When I do not reach for AI first
Scope and priority calls are mine — whether to do the full Module 2 rebuild, what counts as a "small fix" vs. a forbidden feature on this branch. I don't ask AI whether my own fix is "good enough"; I verify it myself.

## My non-negotiables
- Never paste real secrets, API keys, tokens, `.env` contents, credentials, or real personal data into an AI tool — test data only.
- Every diff gets read before it's accepted, not skimmed.
- A claim gets checked against reality — run it, curl it — before I believe it.

## My review rules
- Grade every AI comment honestly (Useful/Noise/Wrong; Valid/False Positive/Noise for security) — not everything flagged is real, and not everything real gets flagged the first time.
- Reproduce before explaining — confirmed via `TestClient`/`curl`, never just a description.
- A green suite isn't proof if it misses the failure mode — 65/65 passing didn't stop two real bugs from shipping earlier.

## What I am still figuring out
- How "read every diff" scales once a codebase is too big to review line-by-line.
- Whether my own review will ever catch what an independent pass catches — so far the instructor caught one bug and a fresh subagent caught another that I missed both times.

## Decision Card
| Decision | My answer |
|---|---|
| **New feature** | Terminal agent (Claude Code) — handles multi-step loops better than one-snippet review. |
| **Code review** | A fresh agent with no memory of writing the code — self-review missed the null bug; an independent pass caught the next one. |
| **Debugging** | Same agent, but only after pasting the exact failing test/error — not a description. |
| **Infrastructure** | Terminal agent for Docker/CI, verified via the real GitHub Actions run — Docker isn't even installed locally, so "should work" was never enough. |
| **Never paste** | Secrets, API keys, tokens, `.env` contents, credentials, real personal data. |
| **One rule** | Ask for an adversarial review before calling anything done — not after a grader asks first. |

**Commitment:** re-read this in 30 days and ask honestly: am I still following it?
