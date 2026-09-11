# Orchestration and Subagents

## When to delegate

Use subagents when parallelization provides real value: independent implementation tasks, independent test development, repository investigation, documentation research, code review, static-analysis investigation. Don't spin up subagents to make the process look more sophisticated than the task needs — a small task done directly is better than a delegated one.

Before delegating any piece of work, define: the objective, the scope, the inputs, the constraints, the expected output, which files/components it may touch, and how its output will be validated. Prefer independent workstreams, and avoid multiple agents editing the same files at once unless the environment explicitly supports safe coordination.

## Orchestration model

You (the primary implementer) stay accountable for task decomposition, dependency management, integration, final correctness, acceptance criteria, and communicating with the user — even when specialists handle research, testing, security review, performance analysis, code review, or isolated implementation slices.

**Subagent output is evidence, not truth.** Verify important claims from a subagent and integrate the work yourself rather than passing it through unchecked. If a subagent says "tests pass," that's a claim to confirm, not a fact to repeat.

## Parallel execution

Tasks may run in parallel only when neither depends on the other's output:

```
Task A ──┐
         ├──> Integration Gate
Task B ──┘
```

Respect any explicit dependency graph from the Sprint document. Never parallelize work that could produce conflicting edits, inconsistent migrations, incompatible API changes, ordering problems, shared-state corruption, or broken intermediate states — in those cases, sequence the work through an integration gate instead.
