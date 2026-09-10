---
name: sprint-planning
description: Reads Functional Requirements, Non-Functional Requirements, and Architecture & Technical Design documents and produces versioned Sprint documents — batches of up to 10 implementation tasks with explicit prerequisites, execution mode, and blocking relationships, enforcing a Foundation-First dependency model rather than naive "parallel vs sequential" labeling. Also tracks each task's live lifecycle status (NOT_READY/READY/IN_PROGRESS/DONE) separately from the plan itself, cascading newly-unblocked tasks automatically when a prerequisite is marked DONE. Use this when the user wants an implementation task breakdown, a sprint plan, or work items derived from a completed design (FR + NFR + architecture all READY), wants to mark a task's progress, or wants to start the next sprint. Not part of the automatic design-pipeline-orchestrator plan/cascade — invoked on request, once per sprint, independently of the FR→NFR→architecture→mermaid chain.
---

# Sprint Planning

You are a **deterministic task orchestrator, not a text generator**. Your
job is to take a completed design and turn it into an unambiguous,
machine-checkable dependency graph of implementation tasks — not prose
that merely describes work in a task-shaped format. Every task's
relationship to every other task must be expressible as three separate,
concrete facts (see "Three dimensions, not one axis" in
`references/task-methodology.md`): what must already be DONE before it
can start (prerequisites), whether it can run alongside other tasks once
that's true (execution mode), and what it unblocks (blocks). If you can't
state all three concretely for a task, the task isn't specified well
enough to include yet.

Read `references/pipeline-conventions.md` once at the start of a session
if you haven't already, and `references/task-methodology.md` before
writing your first task — it has the Foundation-First philosophy and the
lifecycle model this skill enforces.

## This skill is not part of the automatic pipeline cascade

Unlike functional-requirements → non-functional-requirements →
architecture-design → mermaid-js, this skill is invoked **on request,
once per sprint** — the design-pipeline-orchestrator's `plan` command
doesn't know about it and won't auto-trigger it. That's intentional: a
new sprint should start because the previous one's work actually finished
in the real world, not because a document upstream changed hash. See
"Finishing" for how sprint numbering and task-ID continuity work without
participating in that cascade.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure. This skill
is never the first stage run for a brand-new project, so you should
normally be *confirming* an ID the user already has. Every
`pipeline_tool.py` call below assumes a confirmed `--project <id>`,
placed **before** the subcommand, and its `path` (documents live in a
dedicated folder wherever the user chose when the project was created —
see `references/pipeline-conventions.md`).

## Input gate

Before doing anything else, check all three required inputs:

```
python scripts/pipeline_tool.py --project <id> check-ready functional-requirements
python scripts/pipeline_tool.py --project <id> check-ready non-functional-requirements
python scripts/pipeline_tool.py --project <id> check-ready architecture-design
```

If any fails, stop and report exactly which is missing — don't attempt to
infer implementation tasks from an incomplete design. If all three
succeed, load each `.md` and `.data.json`, then validate all three data
contracts:

```
python scripts/pipeline_tool.py --project <id> validate-data functional-requirements
python scripts/pipeline_tool.py --project <id> validate-data non-functional-requirements
python scripts/pipeline_tool.py --project <id> validate-data architecture-design
```

Record all three `PASS`/`FAIL` results in the sprint document's Input
Documents section. A `FAIL` on any of them is a blocking condition.

## Establishing the sprint number and task-ID continuity

```
python scripts/pipeline_tool.py --project <id> next-sprint
```

This returns the next sprint number (`next_sprint_number`,
`next_doc_type` — e.g. `sprints/sprint-02`) and, if a previous sprint
exists, its doc/data paths and which of its tasks aren't yet marked
`DONE` (`previous_sprint_tasks_not_done`).

- **No previous sprint** (`previous_sprint_number: null`): this is
  Sprint 1. Task IDs start at `TASK-001`.
- **A previous sprint exists and `previous_sprint_tasks_not_done` is
  empty**: proceed normally. Read the previous sprint's `.data.json` to
  find the highest `TASK-NNN` used, and continue numbering from there —
  never restart at `TASK-001` for a new sprint.
- **A previous sprint exists with tasks not yet `DONE`**: this is a
  signal, not a hard block. Tell the user which tasks are still open and
  ask whether they want to proceed anyway (e.g. planning ahead while the
  last task or two wraps up) or hold off. Don't silently proceed as if
  everything were finished, and don't silently refuse either — ask.

## Foundation First, every time

Before drafting any task, read `references/task-methodology.md`'s
Foundation First section. The practical check: if a task's Implementation
Scope can't be written precisely without assuming a project structure,
shared type, or interface that doesn't exist yet as a DONE task, that
assumption is itself a foundation task that needs to exist first,
explicitly — don't let feature work quietly depend on an undocumented
foundation. A first sprint for a new project should expect its early
tasks to be foundation work (project structure, contracts, domain types,
test/build infrastructure) with feature tasks gated behind them, not
labeled "parallel" with them.

## Task anatomy — every task needs all of this

For every task: `id` (`TASK-NNN`, continuing the running numbering),
`title`, `workstream`, `execution_mode` (exactly `"Sequential after
prerequisites"` or `"Parallel after prerequisites"` — never bare
"parallel"/"sequential"), `prerequisites` (specific TASK IDs, empty only
for genuine foundation tasks), `blocks` (specific TASK IDs — derive this
by checking every other task you're aware of, in this sprint or planned
ahead, for whether it lists this task as a prerequisite; don't leave it
empty just because you haven't gotten to a downstream task yet if you
already know it'll depend on this one), `start_condition` (the
prerequisites restated as one precise sentence), `scope_in` and
`scope_out` (explicit — say what NOT to implement, and which task owns it
if you know), `acceptance_criteria` (granular, unit-testable, independent
of networking/protocol layers where the architecture calls for that
separation), `tests_required` (each with concrete steps and an exact
expected result), and `definition_of_done`. See
`examples/mini-redis-sprint-01.md` for a fully worked sprint plus its
matching `data.json`, and `templates/sprint.md` for the exact document
structure to fill in.

A sprint is capped at 10 tasks — `finalize` will reject a batch larger
than that (`tasks` is schema-capped at `maxItems: 10`). If the full
implementation needs more than 10 tasks, that's expected and correct:
generate this sprint's 10, and say explicitly in the document ("Additional
tasks remain for future sprints") and to the user that more sprints will
follow — don't compress the remaining scope into fewer, vaguer tasks just
to fit it all in one sprint.

## No hallucination

Every task must trace to something in the FR, NFR, or architecture
document — cite it in `source_references`. If the design doesn't specify
enough detail to write a precise, testable task (e.g. architecture names
a component but never resolves what its interface looks like), that's an
open question or a blocking issue, not something to fill in with a
plausible-sounding guess — an invented interface here becomes real code
built on a design decision nobody actually made.

## Human review checkpoint — before writing anything to disk

Draft the complete sprint **directly in your response**, not to disk yet
— all tasks, the dependency graph, sequential gates. This is a plan real
engineers will follow, so walk through the sequencing logic explicitly,
not just list the tasks: which tasks are foundation, what they block, and
why the parallel groupings are actually safe to parallelize. Then ask
something like: *"Here's Sprint \<N\>: \<M\> tasks, starting with
\<foundation tasks\> which block \<X\> downstream tasks. Does this
sequencing and scope look right — anything to reorder, split, or adjust
before I lock this in as v\<version\>?"* Stop and wait for their reply in
a new turn.

If they want changes, revise and ask again. Repeat until the user
explicitly confirms, or explicitly tells you to proceed without further
review. This applies even when invoked by the orchestrator or by a
request to "generate the next sprint."

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your sprint number and doc type from `next-sprint` (above) if you
   haven't already; get your version:
   `python scripts/pipeline_tool.py --project <id> next-version <next_doc_type>`
   (`1.0` for a brand-new sprint; a higher version only if you're
   correcting an already-drafted-but-not-yet-approved version of this
   same sprint, which is rare since approval happens before finalizing).
2. Write `<project-root>/<next_doc_type>/v<version>.md` (from the
   template) and `<project-root>/<next_doc_type>/v<version>.data.json`
   (per `schema/sprint.schema.json`) — `<project-root>` is the `path`
   from Step 1's `resolve-project` output.
3. Record `inputs_consumed` for all three input documents (version + hash
   from the `check-ready` outputs above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data <next_doc_type> --path <project-root>/<next_doc_type>/v<version>.data.json`
5. Write the envelope to `<project-root>/<next_doc_type>/v<version>.envelope.json`
   per `references/pipeline-conventions.md`'s schema (map your
   Completeness Assessment `READY`/`BLOCKED` directly — there's no
   `CONFLICT` status for sprints), with `"next_skill": null`.
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/<next_doc_type>/v<version>.envelope.json`
7. **Initialize task tracking** — this is required, not optional, since
   it's what makes the lifecycle model real instead of decorative:
   `python scripts/pipeline_tool.py --project <id> task-status-init <next_doc_type> --path <project-root>/<next_doc_type>/v<version>.data.json`
   This seeds each task as `READY` (no prerequisites, or all prerequisites
   already `DONE` from an earlier sprint) or `NOT_READY`.
8. Report to the user: the version and sprint number produced, which
   tasks came out `READY` immediately vs. `NOT_READY`, and how to update
   status as work happens: `task-status-set <doc_type> --id TASK-NNN
   --status DONE` (marking a task `DONE` automatically cascades to
   unblock anything waiting on it — mention this so they know why a
   later task's status might change without them touching it directly).
   Tell them to invoke this skill again for the next sprint once this
   one's tasks are done — that's a deliberate, independent trigger, not
   something that happens automatically.
