# Deterministic task orchestration: methodology reference

Quick reference for the model this skill follows. This is a lookup, not
a tutorial — it's here so every sprint applies the same rules
consistently, not to explain project management from scratch.

## Three dimensions, not one axis

A task's relationship to other tasks is never just "parallel" or
"sequential" — it's three separate questions, and conflating them is
exactly the mistake this skill exists to prevent:

1. **Prerequisites** — what must exist (be DONE) before this task can
   even start. This is about *readiness*, not effort or scheduling.
2. **Execution mode** — once prerequisites are satisfied, can this task
   run alongside others, or must it happen strictly after something
   specific finishes? This is about *concurrency*, and it only applies
   after prerequisites are already met — "parallel" never means "can
   start immediately regardless of what else is going on."
3. **Blocking relationship** — which *later* tasks can't start until
   *this* one is DONE. This is the inverse of prerequisites, stated from
   the other direction, and it's what makes a foundation task's true
   importance visible (a task with many entries in Blocks is a
   bottleneck if delayed, even if it looked small on its own).

A task's full specification needs all three, every time. "TASK-007 can
run in parallel" is an incomplete sentence — parallel with what, once
what is satisfied, and what is waiting on it?

## Foundation First

A foundation isn't a task category like "backend" or "frontend" — it's
the set of things that make every other task even possible to reason
about: project/repo structure, module or package layout, core domain
types and terminology, shared interfaces/contracts, error and result
conventions, and test/build infrastructure. Until these are established,
downstream feature work isn't "blocked" in a mundane scheduling sense —
it's undefined, because there's no shared vocabulary or contract for it
to build against yet.

The practical rule: if a task can't be given a precise, unambiguous
Implementation Scope without first assuming something about project
structure, shared types, or interfaces that doesn't exist yet, it isn't
ready to be written as a task — the thing it's implicitly assuming is
itself a foundation task that needs to exist first, explicitly.

## The lifecycle, and why it's tracked separately from the sprint document

Every task moves through exactly these states, in this order, never
skipping or reversing:

```
NOT READY → READY → IN PROGRESS → DONE
```

- **NOT READY**: at least one prerequisite isn't DONE yet.
- **READY**: every prerequisite is DONE; an engineer can start.
- **IN PROGRESS**: someone's actively working it.
- **DONE**: it meets its Definition of Done, verified by its Tests
  Required.

This lifecycle is tracked in a separate, mutable `status.json` per
sprint (via the `task-status-*` commands), not inside the versioned
sprint document itself. That's deliberate: a task's status changes
constantly as engineers work through it, while the sprint's *content*
(scope, acceptance criteria, dependency structure) should stay stable
once approved — treating every status change as a document revision
would make the version history meaningless noise. See
`references/pipeline-conventions.md` for the mechanics.

Marking a task DONE can make other tasks — in this sprint *or a later
one* — newly READY. The tooling re-derives this automatically
(`task-status-set ... --status DONE` cascades), so don't hand-compute
which tasks unblock; trust the cascade and re-check statuses after any
DONE update.

## What "iterative delivery" means here

Generate exactly one sprint per invocation, capped at 10 tasks. If more
implementation work remains beyond what fits in this sprint, say so
explicitly ("Additional tasks remain for future sprints") rather than
letting the sprint boundary pass silently — the person reading this
sprint should never have to guess whether it's the whole plan or a
slice of it. Task IDs number continuously across sprints (a second
sprint's tasks continue from where the first left off, e.g. TASK-011
onward) — never restart numbering at TASK-001 for a new sprint.
