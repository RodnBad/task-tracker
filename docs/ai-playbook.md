# My Personal AI Playbook

*One page. Written after building and defending Task Tracker end-to-end with AI doing the typing and me doing the deciding.*

## When I reach for AI first
Any task that produces code, tests, or docs — I ask, I don't type it myself; that's every line of this repo. Also for grounding: instead of trusting my memory of a course requirement, I ask AI to find and quote the actual source PDF (this is exactly how the `verify_a.py`/`TaskPriority` gap and the Decision Card's real format both got found — my first draft of both was a guess, not a lookup).

## When I do not reach for AI first
Scope and priority trade-offs are mine, not AI's — whether to do the full Module 2 rebuild, whether "duplicate tags allowed" was worth fixing, what counts as a "small fix" versus a forbidden new feature on this branch. I don't ask AI whether my own fix is "good enough" as a stand-in for verifying it myself.

## My non-negotiables
- Never paste real secrets, API keys, tokens, `.env` contents, credentials, or real personal data (names beyond my own, emails, phone numbers, production logs) into an AI tool — test/demo data only.
- Every diff gets read before it's accepted, not skimmed.
- A claim gets checked against reality — run it, curl it, read the actual response bytes — before I believe it.

## My review rules
- Grade every AI review comment honestly (Useful/Noise/Wrong, or Valid/False Positive/Noise for security) — not everything flagged is real, and not everything real gets flagged the first time (see `docs/final-ai-review.md`'s graded findings).
- Reproduce before explaining: confirmed via `TestClient`/`curl`, never just a description of expected behavior.
- A green test suite isn't proof if it doesn't cover the actual failure mode — 65/65 passing didn't stop two real bugs (null-corruption, zero-width-character bypass) from shipping in earlier commits.

## What I am still figuring out
- How "read every diff" scales once a codebase is too large to review line-by-line — this project stayed reviewable because it stayed small.
- Whether my own self-review will ever catch what an independent pass catches. Evidence so far says no: the instructor's review found the null bug, a fresh adversarial subagent found the zero-width-character variant, and my own first-pass review caught neither.

## Decision Card
| Decision | My answer |
|---|---|
| **New feature** | A terminal agent (Claude Code) — this project showed it handles multi-step loops (model→endpoint→frontend→tests) better than reviewing one generated snippet at a time. |
| **Code review** | A fresh, independent agent with no memory of writing the code — self-review from the same session that wrote it missed the null-corruption bug; an independent pass is what caught the follow-up bug. |
| **Debugging** | Whatever agent I'm already in, but only after I paste the exact failing test output or `curl` response — not a description of the symptom. |
| **Infrastructure** | A terminal agent for Docker/CI, but verified via the CI job's real GitHub Actions run result, not a local claim — Docker isn't even installed on this machine, so "it should work" was never acceptable evidence here. |
| **Never paste** | Real secrets, API keys, tokens, `.env` contents, credentials, and any real person's personal data. |
| **One rule** | Ask for an adversarial review before calling anything done — not after a grader has to ask me first. |

**Commitment:** re-read this page in 30 days and ask honestly: am I still following it?
