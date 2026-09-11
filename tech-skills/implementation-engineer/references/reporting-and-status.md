# Reporting, Status, and Communication

## What good documentation covers

Beyond the final report template in the main SKILL.md, when a design decision is worth recording, capture: the problem, the approach selected, the alternatives considered, the reasoning, and the trade-offs. For each completed task, the report should be able to answer: task ID, status, implementation summary, files/components affected, tests executed, and verification result. List known limitations explicitly rather than letting them go unmentioned, and separate genuine follow-up work (intentionally out of scope) from things that are actually blocking.

## Status discipline

Never mark something COMPLETE just because code was written. Use a status vocabulary that reflects actual evidence — for example: BLOCKED, READY, IN_PROGRESS, IMPLEMENTED, VERIFYING, COMPLETE, FAILED. If the Sprint document defines its own status vocabulary, use that instead of inventing your own. The status should always be traceable to something you actually did or observed, not to intention.

## Communication rules

Be concise but technically precise. Don't expose private chain-of-thought — share conclusions, evidence, decisions, relevant reasoning, and verification results. Use plain, direct language for uncertainty and decisions rather than disguising them as settled facts:

- When something can't be determined from what's available: *"This cannot be determined from the available information."*
- When a decision is genuinely needed: *"This requires a decision because X and Y are both viable and lead to different implementation consequences."*

## No hallucinated completion

Never say "implemented" if code wasn't changed, "tested" if tests weren't run, "verified" if verification didn't happen, "build passes" if the build wasn't run, "dependency is supported" without evidence, or "API exists" without checking. Prefer precise, honest statements even when they're less satisfying — e.g. *"The implementation was added, but the test suite could not be executed because the required runtime is unavailable."*

## Scope discipline

Implement only what the Sprint (or the user's explicit request) actually requires. Don't silently expand scope. If you notice a related problem along the way, decide whether it blocks the current task — fix it only if it does, and otherwise write it down as follow-up work rather than doing opportunistic refactoring nobody asked for.
