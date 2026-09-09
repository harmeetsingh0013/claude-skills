# Design Pipeline Skills

Five Claude Code skills that turn a product idea into a fully specified,
diagrammed system design — each stage gated on the previous one being
genuinely complete, not just present, and built up in small MVP-sized
batches rather than all at once (see section 4).

```
functional-requirements → non-functional-requirements → architecture-design → mermaid-js
                    (coordinated by design-pipeline-orchestrator)
```

| Skill | What it produces | Consumes |
|---|---|---|
| `functional-requirements` | Functional Requirements Document — what the product must do | A product idea |
| `non-functional-requirements` | Non-Functional Requirements Document — performance, scale, security, etc. | The FR document |
| `architecture-design` | System Architecture & Design Document — components, data model, ADRs, tech choices | The FR + NFR documents |
| `mermaid-js` | A set of `.mmd` diagram files | The architecture document's diagram specifications |
| `design-pipeline-orchestrator` | Nothing of its own — decides which of the above need to (re)run | All of the above |

---

## 1. Install

Each skill ships as a `.skill` file, which is a zip archive of a skill
folder. Unzip all five into the same location:

```bash
# Personal — available in every project on this machine
mkdir -p ~/.claude/skills
unzip functional-requirements.skill -d ~/.claude/skills/
unzip non-functional-requirements.skill -d ~/.claude/skills/
unzip architecture-design.skill -d ~/.claude/skills/
unzip mermaid-js.skill -d ~/.claude/skills/
unzip design-pipeline-orchestrator.skill -d ~/.claude/skills/
```

or into a single project's `.claude/skills/` instead of `~/.claude/skills/`
if you only want them there. Keep all five together in the same location —
they refer to each other by name.

Verify with `/skills` in a Claude Code session. You should see all five
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
  new, what should I call it?" A short name (e.g. "url-shortener") becomes
  part of the folder name; the unique ID it mints alongside that is what
  you'll actually use to resume. **Save the ID** — the name alone won't be
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
this skill's installation directory, and **not** relative to wherever
Claude Code happens to be running:

| OS | Location |
|---|---|
| macOS / Linux | `$HOME/<project-name>-<unique-id>/` |
| Windows | `C:\<project-name>-<unique-id>\` |

e.g. `/home/alex/url-shortener-curious-mango/` or
`C:\url-shortener-curious-mango\`. Inside that folder:

```
<project-root>/
  product-idea/
  functional-requirements/
  non-functional-requirements/
  architecture-design/
  mermaid-diagrams/
```

A small registry at `<home-or-C:\>/.design-pipeline/projects.json` maps
each project's unique ID to this folder, which is how `list-projects` and
resuming by ID work without scanning your whole home directory. If the
default location isn't writable in your environment, set the
`DESIGN_PIPELINE_HOME` environment variable to redirect it.

---

## 4. MVP-sized iterations

The pipeline doesn't try to fully specify a product in one pass. Each
round produces a small, reviewable batch instead of everything at once:

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

### `design-pipeline-orchestrator`
Doesn't write anything itself. Resolves the project ID, computes a `plan`
(which stages are stale vs. up to date vs. blocked on something upstream),
and runs the stages that need it, in order, stopping and reporting clearly
if one comes back blocked or in conflict. **Use this by default** — invoke
an individual stage directly only when you know exactly one stage needs to
run and there's no ambiguity about staleness.

### `functional-requirements` (stage 1)
Turns a product idea into a Functional Requirements Document: actors,
scope, and a numbered list of testable requirements (`FR-001`, `FR-002`,
...), each with preconditions, main flow, failure behavior, and
dependencies. Strictly scoped to *what* the system does — it will not name
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
against an NFR capped at 100 concurrent users triggers a `CONFLICT` report
instead of a guess), and requires every consequential decision to follow a
visible chain: **requirement → architectural driver → decision → technology
evaluation → technology choice** — never a straight jump to a technology
name. Produces the full design document plus Architecture Decision Records
(ADRs) and a specification of exactly which diagrams are needed.

### `mermaid-js` (stage 4)
Pure extraction, not design. Reads the architecture document's diagram
specifications and produces one `.mmd` file per requested diagram —
nothing more, nothing invented. Looks for a Mermaid MCP tool first; falls
back to hand-written Mermaid syntax if none is available, and honestly
reports which diagrams were tool-validated versus only manually reviewed.

---

## 6. Typical usage

**Starting a brand-new product:**
> "I want to build a URL shortener for small teams with click analytics.
> Run it through the design pipeline."

The orchestrator will ask if this is new, mint a project ID, and run all
four stages in order (pausing if any stage comes back `BLOCKED` with
questions it needs answered, or reports a conflict between FR and NFR).

**Resuming and making a change:**
> "Project curious-mango — we need to support file uploads now too."

The orchestrator confirms the project exists, updates the product idea,
and re-plans: functional-requirements reruns (new FR), which cascades to
non-functional-requirements, architecture-design, and mermaid-js
automatically — each producing a new version, with unaffected content
carried forward rather than regenerated from scratch.

**Just checking status:**
> "What's the status of curious-mango?"

No stages run — just a report of each stage's current version and whether
anything's stale.

---

## 7. If something stops

- **`BLOCKED`** — a stage couldn't derive something and needs a specific
  question answered (listed explicitly). Answer it and re-run that stage.
- **`CONFLICT`** — architecture-design found a contradiction between FR and
  NFR. Decide which side is wrong (or how to reconcile them), update that
  document, and re-run.
- **`PROJECT_NOT_FOUND`** — the ID you gave doesn't exist. Check for a typo
  or ask for `list-projects` to see what's available.

Nothing in the pipeline silently guesses past one of these — every stop is
reported with the specifics needed to unblock it.
