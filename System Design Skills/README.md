# Design Pipeline Skills

Seven Claude Code skills that turn a raw problem description into a fully
specified, diagrammed system design — and, on request, into a
deterministic implementation task plan. Each design stage is gated on the
previous one being genuinely complete, not just present, and built up in
small MVP-sized batches rather than all at once (see section 4).

```
mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js
                              (coordinated by design-pipeline-orchestrator)
                                                    │
                                                    ▼
                                          sprint-planning (on request)
```

| Skill | What it produces | Consumes |
|---|---|---|
| `mini-prd` | Mini-PRD — problem statement, goals, MVP scope, user journeys, high-level product requirements | A raw problem/idea description (via interview) |
| `functional-requirements` | Functional Requirements Document — what the product must do | The Mini-PRD |
| `non-functional-requirements` | Non-Functional Requirements Document — performance, scale, security, etc. | The FR document (+ the Mini-PRD's workload assumptions) |
| `architecture-design` | System Architecture & Design Document — components, data model, ADRs, tech choices | The FR + NFR documents |
| `mermaid-js` | A set of `.mmd` diagram files | The architecture document's diagram specifications |
| `sprint-planning` | A Sprint document — up to 10 implementation tasks with prerequisites, execution mode, and blocking relationships | The FR + NFR + architecture documents |
| `design-pipeline-orchestrator` | Nothing of its own — decides which design stages need to (re)run | All of the design stages |

---

## 1. Install

Each skill ships as a `.skill` file, which is a zip archive of a skill
folder. Unzip all seven into the same location:

```bash
# Personal — available in every project on this machine
mkdir -p ~/.claude/skills
unzip mini-prd.skill -d ~/.claude/skills/
unzip functional-requirements.skill -d ~/.claude/skills/
unzip non-functional-requirements.skill -d ~/.claude/skills/
unzip architecture-design.skill -d ~/.claude/skills/
unzip mermaid-js.skill -d ~/.claude/skills/
unzip sprint-planning.skill -d ~/.claude/skills/
unzip design-pipeline-orchestrator.skill -d ~/.claude/skills/
```

or into a single project's `.claude/skills/` instead of `~/.claude/skills/`
if you only want them there. Keep all seven together in the same location —
they refer to each other by name.

Verify with `/skills` in a Claude Code session. You should see all seven
listed.

---

## 2. The core idea: documents are contracts, not conversation

Each stage doesn't just write a document and hope the next stage reads it
correctly. Every stage produces **two files**:

- **`vX.Y.md`** — the full, strictly-structured human-readable document
- **`vX.Y.data.json`** — a machine-readable summary of the same content,
  validated against a JSON Schema

Downstream skills read the `.data.json`, not the prose, for anything
structural (requirement IDs, priorities, targets). A schema check
(`validate-data`) confirms the contract actually holds before a document is
trusted, on top of a separate status gate (`check-ready`) that confirms the
upstream skill *claimed* to be done. Both have to pass.

Every document also ends with a **Completeness Assessment** — a
machine-readable verdict (e.g. `READY_FOR_NFR` or `BLOCKED`) that decides
whether the next stage is allowed to run at all. A downstream skill will
refuse to run — not guess, not proceed anyway — if this isn't satisfied.

**None of this replaces you.** Before any stage writes a document to disk
or finalizes it, it drafts the content in the conversation and explicitly
asks whether it's complete and correct — the machine-readable status only
governs what's technically well-formed, not whether it's actually what you
wanted. The orchestrator also checks in with you after each stage
finishes, before moving on to the next one, so you can stop and think
between stages rather than watching the whole pipeline run unattended. If
you'd rather it not stop between stages, just say so ("run the whole
pipeline without stopping to ask me") — each stage will still show you its
draft and ask for sign-off on the content itself, since that's a different
kind of check than pacing.

---

## 3. Projects and versioning

Every run belongs to a **project**, identified by a two-word ID like
`curious-mango`. This is what lets you have several products' pipelines
going at once without them colliding, and what lets you *resume* a project
later rather than starting over.

- **New project:** don't have an ID? Just start talking — the first skill
  you invoke (usually the orchestrator) will ask "new or existing, and if
  new, what should I call it, and where would you like the documents
  saved?" **The location is something you're asked, not something decided
  for you, and there's no hardcoded fallback path** — say a path, or just
  say "use the default" and it'll create the project right in the current
  working directory. A short name (e.g. "url-shortener") becomes part of
  the folder name; the unique ID it mints alongside that is what you'll
  actually use to resume. **Save the ID** — the name alone won't be
  enough to resume, since it's not guaranteed unique on its own.
- **Existing project:** give it your ID. The skill confirms it exists,
  then checks what — if anything — actually needs to be regenerated.
- **Existing project, but you only have a path, not the ID** (copied the
  folder from another machine, lost track of the ID, or the registry got
  wiped): give the skill the path instead. It'll look for that folder,
  register it if it isn't already, and tell you the ID to use from then
  on — it can often recover the original ID straight from the folder name,
  but if it can't, it mints a fresh one and tells you so.

Documents are versioned (`v1.0`, `v1.1`, ...) and **never edited in
place**. A new version is always a new pair of files. Editing an upstream
input (the product idea, an FR, an NFR constraint) and re-running only
regenerates what actually changed, cascading downstream automatically —
you don't need to remember to re-run everything by hand.

All of this lives on disk in a dedicated project folder — **not** inside
this skill's installation directory, and never silently nested inside a
generic subfolder. Where exactly depends on what you said when the
project was created:

- **You gave a location** → the project folder is created there, e.g.
  `~/my-projects/url-shortener-curious-mango/`.
- **You said "use the default"** (or didn't have a preference) → created
  right in the current working directory — wherever the skill happens to
  be running from, e.g. `./url-shortener-curious-mango/` inside whatever
  repo or folder you're already working in, similar to how a `.git`
  folder works.

Inside that folder:

```
<project-root>/
  product-idea/
  mini-prd/
  functional-requirements/
  non-functional-requirements/
  architecture-design/
  mermaid-diagrams/
```

A small registry (`.design-pipeline/projects.json`) tracks every
project's unique ID and where its folder actually is — this is what
`list-projects` and resuming by ID read from. **It follows the same rule
as the project folders themselves**: if a project was created with an
explicit location, its registry entry is still recorded relative to
wherever the skill was run *from* at creation time, and if it was created
with no location (cwd fallback), the registry itself is also local to
that working directory. Practically, this means **a project created with
no explicit location is only discoverable from the same working
directory it was created in** — if `list-projects` or `--project <id>`
comes back empty/not-found and you're confident the ID is right, the
first thing to check is whether you're in a different working directory
than when the project was created, not whether the project was lost.

---

## 4. MVP-sized iterations

The pipeline doesn't try to fully specify a product in one pass. Each
round produces a small, reviewable batch instead of everything at once.
**mini-prd sits outside this — it's a single upfront document, not
produced in batches** (its own "MVP Scope" section, In Scope/Out of
Scope, is what seeds the *first* functional-requirements batch, not a
progression of its own):

- **functional-requirements** picks the ~10 most important requirements
  for this round (a hard ceiling of 12 is schema-enforced — a batch
  that's too big gets rejected, not just discouraged), lists everything
  else it identified as "Deferred to future MVPs," and asks for your
  approval before locking it in.
- **non-functional-requirements** only derives quality attributes for the
  requirements that are new this round — earlier MVPs' NFRs carry forward
  untouched.
- **architecture-design** designs only for what's actually in scope now —
  no speculative infrastructure for deferred requirements that haven't
  been approved yet.
- **mermaid-js** just carries the MVP label through; it doesn't make its
  own scoping decisions.

Every document's `data.json` carries an `mvp` object (`number`,
`is_final`, and for FR/NFR, counts and a `deferred` list) so every stage
— and you — can tell which round something belongs to and whether more
are coming. `is_final: true` only appears once nothing meaningful is left
deferred.

**Extras don't just disappear — they go on a backlog, and the skill tells
you about them.** Anything that doesn't fit in a round's ~10 items is
added to a persistent backlog (`backlog.json` per document type) rather
than silently dropped, and the skill actively surfaces it during review:
*"Here's the top 10 for MVP 1 — I'd also suggest keeping an eye on
\<X, Y, Z\> for later, or I can pull one in now instead."* You can also
add to the backlog directly at any time ("add social login to the
backlog") without triggering a full requirements round. When the next MVP
starts, the skill checks the backlog first, before thinking up anything
new.

Requirement numbering is **cumulative across MVPs**, not reset each round
— MVP 2's new requirements pick up where MVP 1 left off (FR-010, FR-011,
...), and MVP 1's requirements are carried forward unchanged.

Once a full cycle (FR → NFR → architecture → diagrams) finishes, the
orchestrator checks whether anything was deferred and, if so, offers to
start the next MVP — you don't have to remember to ask.

---

## 5. What each skill does

### `mini-prd` (stage 0)
Turns a raw problem/idea description into a Mini-PRD through an active
interview — not a form to fill in silently. Asks one focused question at
a time, following the template's section order (problem statement →
actors → goals → success criteria → MVP scope → user journeys → product
requirements → business rules → analytics → assumptions → constraints →
open questions), and when an answer opens a dependent question, follows
that thread to resolution before moving to the next topic rather than
jumping around. Stays strictly architecture-neutral — it will redirect a
user who starts naming databases or frameworks back toward the underlying
need, and never itself suggests one. Produces the product-level document
every other stage is ultimately grounded in: its In Scope/Out of Scope
split seeds functional-requirements' first batch and backlog, and its
workload assumptions feed non-functional-requirements' capacity targets.

### `functional-requirements` (stage 1)
Turns a Mini-PRD into a Functional Requirements Document: actors,
scope, and a numbered list of testable requirements (`FR-001`, `FR-002`,
...), each with preconditions, main flow, failure behavior, and
dependencies. Its first batch is seeded from the Mini-PRD's In Scope list
and `PR-NNN` product requirements (each `FR-NNN` records which `PR-NNN`
it elaborates); the Out of Scope list seeds the backlog immediately.
Strictly scoped to *what* the system does — it will not name
a database, an API shape, or a cloud service; those are scope creep at
this stage and are pushed to architecture-design instead.

### `non-functional-requirements` (stage 2)
Turns the FR document into quality-attribute requirements: performance,
scalability, availability, durability, security, compliance, and more —
each one (`NFR-001`, ...) explicitly traced back to the FR(s) that implied
it. Also technology-agnostic: an NFR says "99.999999999% durability," never
"use S3."

### `architecture-design` (stage 3)
The one stage allowed to make real decisions — databases, queues, APIs,
cloud services. Requires *both* FR and NFR documents, cross-checks them for
contradictions before designing anything (e.g. an FR implying 10M users
against an NFR capped at 100 concurrent users triggers a hard-blocking
`BLOCKED` status instead of a guess), and requires every consequential
decision to follow a visible chain: **requirement → architectural driver →
decision → technology evaluation → technology choice** — never a straight
jump to a technology name.

Operates like a principal architect (techniques from Fowler, Booch,
Kleppmann, and Richards & Ford — applied as engineering discipline, never
as a voice to imitate): **depth adapts to actual complexity and risk, not
a fixed checklist** — a simple system gets a short, honest document with
sections explicitly marked "Not Applicable" where padding would otherwise
go; a genuinely complex distributed system gets real depth where the
complexity actually is. Every statement is kept classified as a
Requirement, a Derived fact, an Assumption, a Decision, or an Unknown —
never blurred together — and the document ends in exactly one of three
states: `READY_FOR_IMPLEMENTATION_PLANNING`, `READY_WITH_ASSUMPTIONS`
(the common, non-degraded case), or `BLOCKED`. This skill designs; it
never writes implementation code, breaks work into modules or tasks
(that's `sprint-planning`), and — deliberately — **never produces
diagrams or diagram specifications at all**; that's entirely `mermaid-js`'s
job now, working from this document's content directly.

Produces the full design document plus concise Architecture Decision
Records (Context / Decision / Alternatives / Trade-offs).

### `mermaid-js` (stage 4)
Pure extraction, not design — and not a checklist either. There's no
diagram spec to read anymore: this skill reads architecture-design's
actual content (System Context, Component Architecture, Request Flows,
Data Model, Deployment Architecture) and decides for itself which
diagrams that content actually warrants, skipping any type a section
doesn't support (a "Not Applicable" caching section produces no caching
diagram). Looks for a Mermaid MCP tool first; falls back to hand-written
Mermaid syntax if none is available, and honestly reports which diagrams
were tool-validated versus only manually reviewed — and *why* a diagram
type was skipped, not just that it was.

### `sprint-planning` (on request, not a numbered pipeline stage)
Turns a completed design (FR + NFR + architecture-design all `READY`)
into implementation tasks — up to 10 per sprint, each with explicit
prerequisites, execution mode, and blocking relationships, plus a tracked
`NOT_READY → READY → IN_PROGRESS → DONE` lifecycle. Invoked independently
per sprint, not chained automatically. See section 6 for the full model.

### `design-pipeline-orchestrator`
Coordinates the five design stages above (not `sprint-planning`, which it
can point you to but doesn't chain into automatically). Resolves the
project ID, computes a `plan`, and runs whatever's stale, in order,
stopping and reporting clearly if something comes back blocked or in
conflict. **Use this by default** for the design stages — invoke an
individual one directly only when you know exactly which one needs to run.

---

## 6. sprint-planning: deterministic task orchestration

Once FR, NFR, and architecture-design are all `READY`, `sprint-planning`
turns the design into implementation work — but it's a **deterministic
task orchestrator, not a text generator**. It's invoked independently, on
request, once per sprint; it is not part of the automatic
design-pipeline-orchestrator cascade, because a new sprint should start
when the previous one's work actually finished, not when a document
upstream changed hash.

**Three separate facts per task, never collapsed into "parallel vs.
sequential":**
1. **Prerequisites** — what must already be `DONE` before this task can start.
2. **Execution mode** — once prerequisites are met, can it run alongside
   other tasks, or must it wait for something specific? ("Parallel" never
   means "can start immediately regardless of prerequisites.")
3. **Blocks** — which later tasks are waiting on this one.

**Foundation First.** Project structure, shared interfaces, core domain
types, and test/build infrastructure aren't a task category — they're what
makes every other task's scope even well-defined. Feature work stays
`NOT_READY`, not "parallel," until the foundation it silently depends on
is actually `DONE`.

**A real, tracked lifecycle**, separate from the sprint document itself
(so marking progress doesn't churn a version bump every time):
```
NOT READY → READY → IN PROGRESS → DONE
```
`task-status-init` seeds every task's starting status from its
prerequisites (checked across *every* sprint, not just the current one).
`task-status-set ... --status DONE` automatically cascades — any task
anywhere whose prerequisites just became fully satisfied flips from
`NOT_READY` to `READY` without you having to compute that by hand.

**Capped and cumulative, like the design stages.** A sprint contains at
most 10 tasks (schema-enforced, not just a suggestion) and task IDs number
continuously across sprints — Sprint 2 continues from Sprint 1's highest
`TASK-NNN`, never restarting. If more work remains than fits in one
sprint, the document says so explicitly rather than compressing the rest
in to fit.

---

## 7. Typical usage

**Starting a brand-new product:**
> "I want to build a URL shortener for small teams with click analytics.
> Run it through the design pipeline."

The orchestrator will ask if this is new, mint a project ID, and start
with `mini-prd` — a real interview about the problem, actors, goals, and
MVP scope, one question at a time — before running the remaining four
stages in order (pausing if any stage comes back `BLOCKED` with
questions it needs answered, or reports a conflict between FR and NFR).

**Resuming and making a change:**
> "Project curious-mango — we need to support file uploads now too."

The orchestrator confirms the project exists and asks whether this is a
Mini-PRD-level change (a new capability the product brief didn't cover)
or a smaller edit to an existing FR/NFR document. For a Mini-PRD-level
change, mini-prd revises first, which cascades all the way down:
functional-requirements reruns, then non-functional-requirements,
architecture-design, and mermaid-js — each producing a new version, with
unaffected content carried forward rather than regenerated from scratch.

**Just checking status:**
> "What's the status of curious-mango?"

No stages run — just a report of each stage's current version and whether
anything's stale.

---

## 8. If something stops

- **`BLOCKED`** — a stage couldn't derive something and needs a specific
  question answered (listed explicitly). Answer it and re-run that stage.
- **`CONFLICT`** — architecture-design found a contradiction between FR and
  NFR. Decide which side is wrong (or how to reconcile them), update that
  document, and re-run.
- **`PROJECT_NOT_FOUND`** — the ID you gave doesn't exist. Check for a typo
  or ask for `list-projects` to see what's available.

Nothing in the pipeline silently guesses past one of these — every stop is
reported with the specifics needed to unblock it.
