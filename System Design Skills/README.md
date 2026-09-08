# Design Pipeline Skills

Five Claude Code skills that turn a product idea into a fully specified,
diagrammed system design — each stage gated on the previous one being
genuinely complete, not just present.

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
  you invoke (usually the orchestrator) will ask "new or existing?" and
  mint one for you (`resolve-project`). **Save this ID** — it's the only
  way to resume the project later.
- **Existing project:** give it your ID. The skill confirms it exists,
  then checks what — if anything — actually needs to be regenerated.

Documents are versioned (`v1.0`, `v1.1`, ...) and **never edited in
place**. A new version is always a new pair of files. Editing an upstream
input (the product idea, an FR, an NFR constraint) and re-running only
regenerates what actually changed, cascading downstream automatically —
you don't need to remember to re-run everything by hand.

All of this lives on disk under:

```
design-docs/<project-id>/
  product-idea/
  functional-requirements/
  non-functional-requirements/
  architecture-design/
  mermaid-diagrams/
```

---

## 4. What each skill does

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

## 5. Typical usage

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

## 6. If something stops

- **`BLOCKED`** — a stage couldn't derive something and needs a specific
  question answered (listed explicitly). Answer it and re-run that stage.
- **`CONFLICT`** — architecture-design found a contradiction between FR and
  NFR. Decide which side is wrong (or how to reconcile them), update that
  document, and re-run.
- **`PROJECT_NOT_FOUND`** — the ID you gave doesn't exist. Check for a typo
  or ask for `list-projects` to see what's available.

Nothing in the pipeline silently guesses past one of these — every stop is
reported with the specifics needed to unblock it.
