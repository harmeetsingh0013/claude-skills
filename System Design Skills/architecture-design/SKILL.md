---
name: architecture-design
description: Produces a versioned system-design/architecture document using a Domain-Driven Design approach — ubiquitous language, bounded contexts, context mapping, and tactical design (aggregates, entities, domain events) — plus components, data architecture, APIs, ADRs, security, scalability, resilience, and Mermaid diagram specifications. Stage 3 of a five-stage design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js), built from FR and NFR documents. Use for system architecture, technical design, ADRs, domain modeling, bounded contexts, or technology/component decisions for a product with FR/NFR documents, or to run/update the "architecture design" stage. Also use when re-invoked by design-pipeline-orchestrator. The one pipeline stage that makes technology and domain-modeling decisions — but never produces implementation code itself. Does not produce a module/task breakdown — that's a separate skill.
---

# Architecture Design

You approach this the way Eric Evans' *Domain-Driven Design* does: start
from the domain (what the FR/NFR documents actually describe), find its
natural seams (bounded contexts), give each a precise shared vocabulary
(ubiquitous language), and only then get concrete about aggregates,
technology, and components — never the other way around. This is the only
pipeline stage where naming a database, a queue, a cloud service, or an
API shape is correct rather than scope creep — but every decision here
should trace back to something in the FR or NFR document, not to habit or
default preference. Read `references/pipeline-conventions.md` once at the
start of a session if you haven't already.

**You design; you don't implement.** Bounded contexts, aggregates, domain
events, and components are described in prose and structured data —
never as class definitions, method signatures, interface code, or
database DDL. This document's bounded contexts are meant to become the
input to a separate module/task-breakdown skill later; writing the
implementation yourself, or breaking work into tasks yourself, would
pre-empt that step, not help it.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID or a path to existing documents,
otherwise ask the user whether it's new/existing/a path, then confirm via
`resolve-project`). This skill is never the
first stage run for a brand-new project, so you should normally be
*confirming* an ID the user already has. Every `pipeline_tool.py` call
below assumes a confirmed `--project <id>`, placed **before** the
subcommand, and its `path` (documents live in a dedicated folder under
the user's home directory, or `C:\` on Windows — see
`references/pipeline-conventions.md` — not wherever this session happens
to be running).

## Input gate

Before doing anything else, check *both* required inputs:

```
python scripts/pipeline_tool.py --project <id> check-ready functional-requirements
python scripts/pipeline_tool.py --project <id> check-ready non-functional-requirements
```

If either fails, stop and report exactly which is missing, in this form:

```
ERROR:
Architecture Design requires both:
1. Functional Requirements Document
2. Non-Functional Requirements Document
```

only naming the one(s) that actually failed. Don't attempt to fill the gap
by inventing requirements or by asking the user to restate them from
scratch — the correct fix is to run the missing upstream skill.

If both succeed, load each `.md` and `.data.json`, then validate both data
contracts:

```
python scripts/pipeline_tool.py --project <id> validate-data functional-requirements
python scripts/pipeline_tool.py --project <id> validate-data non-functional-requirements
```

Record both `PASS`/`FAIL` results in Section 2 (Input Documents) of your
document. A `FAIL` on either is a blocking condition — don't design against
a structurally broken contract even if its status claimed READY.

Also check for a Mini-PRD, informatively (not a required gate — the two
checks above are the only hard requirements): `python scripts/pipeline_tool.py --project <id> latest mini-prd`.
Its Section 10 (Constraints) is a legitimate source of architecture
drivers that would never otherwise surface in FR (behavioral) or NFR
(quality-attribute) documents — a regulatory constraint, a mandate to use
existing infrastructure, a real budget ceiling. If it exists, read its
constraints and let genuine ones inform an ADR the normal way (see "The
reasoning chain" below); if it doesn't exist (an older project, or this
skill run standalone), proceed without it.

Then check that the two documents are talking about the **same MVP
round**: compare `mvp.number` in the FR document's `data.json` against
`mvp.number` in the NFR document's `data.json`.

- **They match** → proceed normally.
- **They don't match** (most commonly: FR is ahead, e.g. FR shows
  `mvp.number: 2` but NFR still shows `mvp.number: 1`) → stop. Report:
  `ERROR: Functional Requirements is at MVP <X> but Non-Functional
  Requirements is still at MVP <Y> — run non-functional-requirements again
  before architecture-design.` `check-ready` alone won't catch this,
  because NFR's older version is still legitimately `READY` — it's just
  stale relative to FR's newer MVP round, and designing against a
  mismatched pair would silently mix scopes from two different rounds.

## Validate before designing: conflict detection

Once both inputs pass validation, read them fully before writing anything,
and actively look for contradictions between them — don't take both
documents at face value just because they each individually passed. The
classic case: an FR implies a user/traffic scale the NFR document doesn't
support (or contradicts), e.g. "supports 10 million users" in FR against
"100 concurrent users" in NFR. Other contradictions are just as real: an
NFR latency target that's incompatible with an FR's described workflow, or
an NFR durability/compliance requirement an FR's described data flow can't
satisfy as written. Cross-reference by ID (FR-N's requirements array
against NFR-N's `related_fr`) — the structured data makes this a lot more
reliable than eyeballing prose.

If you find a genuine contradiction:

- Do not silently pick one side and design around it.
- Do not average or split the difference.
- Record it in Section 3 (Requirements Validation → Conflicts).
- Set the Completeness Assessment to `CONFLICT`, the envelope's `status` to
  `CONFLICT`, and add one `errors` entry per contradiction with
  `code: "CONFLICT_DETECTED"` and a plain-language `message` describing
  both conflicting statements and where they came from (FR-N vs NFR-N).
- Still write a document — but make it a short report of the conflict(s)
  rather than a full design, and still call `finalize`. A clearly reported
  conflict is a legitimate, useful pipeline output; a design built on an
  unresolved contradiction is not.

If no conflicts, proceed to design.

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version architecture-design`.
If it returns a `previous_doc_path`/`previous_data_path`, read both as your
baseline. Change only what the new/changed FR or NFR content actually
affects — preserve ADRs and decisions that remain valid, and add a new ADR
(don't silently rewrite an old one — mark the old one `Superseded by
ADR-N`) if a decision needs to change. Note what changed and why in the
envelope's `summary`.

## Design only for the current MVP's scope

Read the `mvp.number` from both the FR and NFR documents' `data.json` —
they should match (the NFR document is built from that same FR round). Set
your own `mvp.number` to the same value.

Design for what's actually in scope now, not for requirements sitting in
the FR document's "Deferred to future MVPs" list. It's tempting to
future-proof — add the queue now because "we'll need it for MVP 3 anyway"
— but that's speculative architecture based on requirements that haven't
been approved yet and might change before they're actually scoped. If a
past MVP's ADR already covers something the current MVP still needs,
reuse it (that's normal and expected); just don't add new infrastructure
or components in anticipation of work that isn't real yet. This is also
what keeps this stage's output proportional to the FR/NFR batch size,
rather than growing into a full system design on the first round.

Set `mvp.is_final` to true only when both input documents' `mvp.is_final`
are true.

## Domain-Driven Design approach

Do strategic design before tactical design, and tactical design before
technology decisions — in that order, every time. See
`references/ddd-glossary.md` for full definitions of every term below and
the heuristics for finding boundaries.

**1. Ubiquitous Language.** Pull the vocabulary the FR/NFR documents
already use — don't invent new names for things they named. If a term
means different things in different areas (the same word "Team" used for
two different concepts, say), that's an early signal you're looking at
more than one bounded context.

**2. Bounded Contexts (strategic design).** Partition the system using
the FR document's capability groupings, differing NFR profiles (a
strict-consistency/low-latency area vs. an eventually-consistent one is a
strong hint), vocabulary splits, and natural ownership boundaries. Each
bounded context is naturally a unit a future module/task-breakdown skill
would work from, so favor a small number of clearly-scoped contexts over
many overlapping ones — but breaking that down into modules or tasks is
that separate skill's job, not something you produce here.

**3. Context Map (strategic design).** For every pair of bounded contexts
that interact, name the relationship using one of the DDD context-mapping
patterns (Partnership, Shared Kernel, Customer-Supplier, Conformist,
Anticorruption Layer, Open Host Service, Published Language, Separate
Ways) with a stated rationale. Don't leave a relationship unlabeled, and
don't invent a pattern name that isn't one of these.

**4. Tactical Design.** Within each bounded context, name its aggregates
(aggregate root, entities, value objects, invariants) and its domain
events. An aggregate's boundary is also its transactional consistency
boundary — this is where an NFR's consistency/concurrency requirement
becomes concrete. Cross-aggregate and cross-context consistency is
eventual, coordinated through the domain events you name here — which is
usually also the mechanism behind a Published Language or Open Host
Service relationship in the context map.

**5. Only then, technology and component decisions** — see "The reasoning
chain" below, which now operates *within* the bounded contexts and
aggregates you've just defined rather than against the raw FR/NFR list.

Bounded contexts should be genuinely stable across MVPs (see "Design only
for the current MVP's scope" above) — most rounds add aggregates or
tactical detail to an existing context, not new contexts. If you find
yourself redrawing context boundaries every round, that's usually a sign
the boundaries weren't right the first time, not that the product
genuinely changed shape.

## The reasoning chain: never skip straight to a technology

Every consequential decision should visibly follow:
**FR + NFR → architectural driver → architecture decision → technology
evaluation → technology decision.** See
`references/architecture-reasoning.md` for a full worked example (click
tracking → async event publication → queue technology choice). Collapsing
this into "we use Kafka because click tracking" is architecture invention,
not architecture design — it also makes the decision impossible to
revisit intelligently when a requirement changes later.

## What belongs in this document

Fill in `templates/architecture-design.md` exactly — it has 35 numbered
sections plus an MVP Scope note and a Completeness Assessment; don't drop
or reorder them, even if a section ends up brief. Use
`references/ddd-glossary.md` for DDD terminology and patterns,
`references/adr-format.md` for each ADR entry, and
`references/architecture-reasoning.md` for the driver chain. See
`examples/url-shortener-architecture.md` for a fully worked excerpt
(including the DDD sections) plus its matching `data.json`.

Section 35 (Mermaid Diagram Specification) is where you tell `mermaid-js`
what to produce: name, type, and what each diagram must show. List only
the diagrams this specific design actually warrants — not one of every
type by default, and not diagrams for deferred, not-yet-in-scope work. A
`context-map` diagram is usually worth including once you have more than
one bounded context.

This document does not include a module or task breakdown — bounded
contexts are a natural starting point for one, but producing it is a
separate skill's job, not this one's.

Alongside the `.md`, produce a `.data.json` following
`schema/architecture-design.schema.json` — ubiquitous language, bounded
contexts, the context map, domain events, ADRs, components, diagram
specifications, and traceability all need structured entries, not just
prose. This is the contract `mermaid-js` will read.

## No hallucination

If a requirement is too vague to make a specific technology decision (e.g.,
NFR says "must scale" with no number), don't pick a technology to sound
decisive — note the gap in "Open Questions" and either make an explicitly
labeled assumption (stated as such, so it's easy to revisit) or set the
Completeness Assessment to `BLOCKED` if the gap is significant enough that
any design would be a guess.

## Completeness Assessment

```
Architecture status:
READY_FOR_MERMAID
```

or

```
Architecture status:
BLOCKED

Blocking issues:
- ...
```

or, if Section 3 found contradictions:

```
Architecture status:
CONFLICT

Conflicts detected:
- CONFLICT_DETECTED: FR-N says ... while NFR-N says ...
```

Set the same value in `data.json`'s `status` field
(`READY_FOR_MERMAID`, `BLOCKED`, or `CONFLICT`).

## Human review checkpoint — before writing anything to disk

This is the stage with the most consequential decisions in the whole
pipeline — bounded context boundaries and technology choices are both
expensive to unwind later, and the user may have constraints (a preferred
cloud provider, an existing system to integrate with, a team's existing
expertise, or a different sense of where the domain's natural seams are)
that never showed up in the FR or NFR documents because nothing asked
about them there.

Draft the full document **directly in your response**, not to disk yet.
At minimum, walk through the bounded contexts and context map (the
strategic design — this is often the more consequential thing to get
right, and the easiest to fix early), then the key ADRs, not just a
"done!" — the user needs enough to actually evaluate it. Then explicitly
ask something like: *"Here's the architecture design: I've split this
into \<N\> bounded contexts — \<names\> — connected as \<brief context map
summary\>. Does that domain split make sense, or would you carve it up
differently? And here are the key technology decisions in ADR-1 through
ADR-N — do these work for you, or any constraints I should account for,
before I lock this in as v\<version\> and hand off to diagram
generation?"* Stop and wait for their reply in a new turn — don't write
files or finalize in the same turn you present the draft.

If they push back on a bounded context boundary, that's a strategic-design
change — revise sections 4-6 (and everything downstream that references
them) before moving on, rather than patching around it in the tactical or
technology sections. If they push back on a technology decision, treat
that the same way you'd treat a new constraint: revise the relevant ADR
(superseding it, not silently editing it, per `references/adr-format.md`)
and ask again. Repeat until the user explicitly confirms this version, or
explicitly tells you to proceed without further review. This applies even
when the orchestrator invoked you.

If your Completeness Assessment is `CONFLICT`, present the conflict report
itself for this checkpoint — the question becomes "which side should
change, or how would you like to reconcile this?" rather than "does this
design look right?"

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version architecture-design`
2. Write `<project-root>/architecture-design/v<version>.md` and
   `<project-root>/architecture-design/v<version>.data.json`
   (`<project-root>` is the `path` from Step 1's `resolve-project` output).
3. Record `inputs_consumed` for both `functional-requirements` and
   `non-functional-requirements` (version + hash from the `check-ready`
   output above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data architecture-design --path <project-root>/architecture-design/v<version>.data.json`
5. Write the envelope to `<project-root>/architecture-design/v<version>.envelope.json`,
   mapping your Completeness Assessment status per
   `references/pipeline-conventions.md`'s table, with
   `"next_skill": "mermaid-diagrams"` (set this even on `CONFLICT` status,
   since re-running after the conflict is resolved still leads there).
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/architecture-design/v<version>.envelope.json`
7. Report to the user the version produced, a short summary, whether any
   conflicts were found, and whether `mermaid-js` can now run — report
   this even if the orchestrator invoked you, rather than silently
   continuing.
