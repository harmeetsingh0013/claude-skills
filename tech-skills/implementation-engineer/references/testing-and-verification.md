# Testing, Quality, and Verification

## Testing strategy

Tests should verify behavior, not implementation details. Use whatever combination actually fits the change: unit, integration, contract, component, end-to-end, concurrency, migration, and — where justified — performance tests. Follow whatever tests the Sprint document explicitly requires, and make sure every acceptance criterion has a clear answer to "how is this verified?"

## Test quality

Don't write tests to inflate a coverage number. A good test demonstrates expected behavior, meaningful boundary conditions, failure behavior, and relevant invariants. Include negative cases when they materially affect correctness. For concurrency code specifically, test the race, cancellation, ordering, timeout, and failure scenarios you identified in `concurrency.md` — not just the happy path.

## Code quality tooling

Use whatever quality tools the technology stack (or existing repo conventions) call for. Don't assume one project's toolset (e.g. a Java/Spring project's JUnit + JaCoCo + PMD + Spotless) generalizes to every project in that language — determine the right tooling from project requirements, existing repo conventions, the approved Technology Stack, and official documentation, in that order. Don't add tooling without a reason.

## The verification gate

Before declaring anything complete, actually check:

**Build** — the project builds; dependency resolution succeeds; generated artifacts are valid.

**Tests** — required tests pass; relevant existing tests still pass; new tests pass.

**Static quality** — configured linters, formatters, and static analysis pass.

**Behavior** — acceptance criteria are satisfied; error paths behave correctly; compatibility requirements hold.

**Repository integrity** — no accidental files, no unrelated changes, no secrets introduced, no leftover debug code.

## Definition of Done

A task is COMPLETE only when: implementation is finished, acceptance criteria are satisfied, required tests exist and pass, required quality checks pass, no known blocking issue remains, the implementation is consistent with the approved architecture, documentation is updated where required, and the task's status has been updated. If any of these aren't true, don't claim completion — use the status vocabulary in `reporting-and-status.md` instead.

## Handling failures

When a test or quality gate fails, understand it before touching code. Classify it first: implementation defect, test defect, environment problem, dependency problem, flaky behavior, pre-existing failure, or requirement inconsistency — then address the actual cause. Never weaken a test to force a green build, never delete a failing test without a genuinely justified reason, and never hard-code a special case purely to satisfy a test.

## Pre-existing failures

If the repo already has failing tests or quality issues unrelated to your task, don't silently absorb them into your change or falsely attribute them to your own work — determine whether they're related, pre-existing, or caused by your implementation, and report the distinction explicitly.

## Final review checklist

Before wrapping up a task or sprint, walk through:

- **Requirements** — Did we implement what was asked? Did we satisfy every acceptance criterion?
- **Architecture** — Does this fit the existing architecture? Did it introduce unnecessary coupling?
- **Code quality** — Is it understandable? Are the abstractions justified? Any new duplication?
- **Concurrency** — Is shared state safe? Is concurrency bounded? Is cancellation handled? Are failure modes understood?
- **Testing** — Are the important behaviors covered? Do the tests verify behavior rather than implementation details?
- **Dependencies** — Did we add anything unnecessary? Is everything stable and non-deprecated?
- **Security** — Any obvious security issue introduced? Are sensitive values protected?
- **Operations** — Can this be diagnosed in production? Are failures observable?
- **Scope** — Did we touch anything unrelated to the task?
