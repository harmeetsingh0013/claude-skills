# implementation-engineer

A Claude skill that turns an approved software-engineering plan (a Sprint document, ticket, or task list) plus an approved technology stack into a production-quality, tested, verified implementation in a real repository — operating with the discipline of a Senior/Staff-level engineer.

## What it does

When this skill triggers, Claude:

- Runs every task through a lifecycle: **Discover → Validate → Plan → Implement → Test → Verify → Review → Document → Update Status**.
- Refuses to invent requirements or technology choices — it follows a strict source-of-truth hierarchy (user requirements → Sprint doc → Tech Stack doc → architecture docs → repo conventions → official docs → tests → other sources).
- When the Sprint or Tech Stack documents are missing, it doesn't guess: it checks the repo/docs first, then falls back to inspecting an existing source-code path as evidence (without treating anything it observes there as automatic authorization for new choices), and only interviews the user directly as a last resort.
- Never claims a build passed, a test passed, or something was "verified" unless it actually ran and confirmed it.
- Surfaces material decisions (architecture, technology, contracts, persistence, security) to the user instead of resolving them silently.
- Closes out work with an honest status report — using a real Definition of Done, not "I wrote some code."

## When it triggers

Use it for: implementing a feature/ticket/sprint task, writing production code against an existing codebase, turning a design or architecture doc into working code, executing a multi-step engineering task that needs tests and verification, or picking up a partially-finished change.

It's not meant for throwaway scripts, one-off snippets, or pure explanation/teaching requests with no repository involved.

## File structure

```
implementation-engineer/
├── SKILL.md                                   Identity, absolute rules, source-of-truth hierarchy,
│                                               the lifecycle, and pointers to the reference files below.
└── references/
    ├── engineering-principles.md              Pragmatic-programmer principles, clean code, design
    │                                           patterns, anti-patterns, language/paradigm guidance,
    │                                           API/contract discipline, DB/persistence discipline.
    ├── concurrency.md                          Correctness checklist for concurrent/async code.
    ├── source-of-truth-and-decisions.md        Evidence rules, the missing-requirements decision tree
    │                                           (docs → source code as evidence → interview),
    │                                           technology-selection constraint, dependency policy,
    │                                           decision protocol, research protocol.
    ├── orchestration-and-subagents.md          When/how to delegate, parallel-execution safety rules.
    ├── testing-and-verification.md             Test strategy/quality, quality tooling, the verification
    │                                           gate, Definition of Done, failure handling, final review
    │                                           checklist.
    ├── security-observability-performance.md   Security, observability, and performance considerations.
    └── reporting-and-status.md                 Report content, status vocabulary, communication rules,
                                                scope discipline.
```

`SKILL.md` stays short (~150 lines) and always loads when the skill triggers. The `references/` files are pulled in only as the task needs them — e.g. `concurrency.md` only matters once concurrent/async code is actually on the table.

## Why one skill instead of several

Every section of the source requirements document serves a single workflow — turning an approved plan into verified, working code — rather than several independent jobs a user would invoke separately. Splitting it into multiple skills would fragment one coherent lifecycle across skill boundaries; instead, the depth is managed with progressive disclosure (a lean `SKILL.md` plus topic-specific reference files) rather than by splitting into multiple skills.

## Status

- Drafted from a full requirements spec (Senior Software Engineer implementation skill).
- Missing/incomplete-requirements handling expanded to include a source-code-as-evidence sub-flow (inspect an existing repo before falling back to a user interview).
- Qualitative test pass completed (3 test prompts covering: an unambiguous task, a task with a hidden material decision, and a task where the user asked to skip verification). No formal eval/assertion set — this skill's output is context-dependent (real code against a real repo), so verification was qualitative human review rather than fixed assertions.

## Installing

Use the **Save skill** button on the delivered `.skill` file (or `SKILL.md`), or drop the `implementation-engineer/` folder into your skills directory if you're managing skills manually.
