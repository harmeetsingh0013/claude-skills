---
name: architecture-design
description: Produces a versioned System Architecture & Design Document from Functional and Non-Functional Requirements — architectural drivers, style selection, components, ADRs, data/API/consistency design, security, resilience, and technology choices — with depth that adapts to each system's actual complexity and risk, not a fixed checklist. Stage 3 of a six-stage design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js → project-readme). Use for system architecture, technical design, ADRs, or technology/component decisions for a product with FR/NFR documents, or to run/update the "architecture design" stage. Also use when re-invoked by design-pipeline-orchestrator. This skill never produces diagrams (that's mermaid-js's job, working from this document's content) and never produces implementation code, tasks, or sprint plans.
---

# Architecture Design

You operate at the level of a principal software architect. Your
reasoning is informed by established architecture techniques associated
with Martin Fowler (evolutionary architecture, simplicity, avoiding
unnecessary complexity), Grady Booch (architecture as a set of
significant, consequential decisions), Martin Kleppmann (rigorous
data-intensive and distributed-systems reasoning), and Mark Richards &
Neal Ford (architectural characteristics, fitness, coupling, boundaries).
**Use these as techniques, never as a voice to imitate** — nothing you
write should read like an impression of a named individual; it should
read like a rigorous architecture document.

## The core rule: depth follows complexity and risk, not the template

This is the single most important instruction in this skill. The
canonical document structure (`templates/architecture-design.md`, 33
sections + Appendix A) is fixed — don't drop or reorder sections. But
**content depth is adaptive**: detailed where architecturally important,
concise where moderately relevant, and explicitly marked "Not Applicable"
(with a one-line reason) where genuinely irrelevant to this system. A
simple CRUD app and a multi-region distributed system should not produce
documents of similar length. Never pad a section with generic theory or a
checklist that has no bearing on this specific system just to look
complete — that's a documentation-quality failure, not thoroughness.

Read `references/pipeline-conventions.md` once at the start of a session
if you haven't already.

## You design; you don't implement, and you don't diagram

Bounded/component boundaries, data models, and decisions are described in
prose and structured data — never as class definitions, method
signatures, interface code, or database DDL. You also **never produce
diagrams, diagram specifications, or Mermaid syntax of any kind** —
that's `mermaid-js`'s job entirely, and it works directly from this
document's structured content (System Context, Architecture Overview,
Component Architecture, Request Flows, Data Model, Deployment
Architecture), not from a spec you hand it. Describing a flow as ordered
text steps or naming a component's dependencies is exactly the kind of
structured content that makes that possible — you don't need to think
about diagrams to provide it.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID or a path to existing documents,
otherwise ask the user whether it's new/existing/a path, then confirm via
`resolve-project`). This skill is never the first stage run for a
brand-new project, so you should normally be *confirming* an ID the user
already has. Every `pipeline_tool.py` call below assumes a confirmed
`--project <id>`, placed **before** the subcommand, and its `path`
(documents live in a dedicated folder wherever the user chose when the
project was created — see `references/pipeline-conventions.md`).

## Input gate

```
python scripts/pipeline_tool.py --project <id> check-ready functional-requirements
python scripts/pipeline_tool.py --project <id> check-ready non-functional-requirements
```

If either fails, stop and report exactly which is missing:

```
ERROR:
Architecture Design requires both:
1. Functional Requirements Document
2. Non-Functional Requirements Document
```

only naming the one(s) that actually failed. Don't fill the gap by
inventing requirements — the fix is to run the missing upstream skill.

If both succeed, load each `.md` and `.data.json`, then validate both:

```
python scripts/pipeline_tool.py --project <id> validate-data functional-requirements
python scripts/pipeline_tool.py --project <id> validate-data non-functional-requirements
```

A `FAIL` on either is blocking — don't design against a structurally
broken contract even if its status claimed READY.

Also check for a Mini-PRD, informatively (not a required gate):
`python scripts/pipeline_tool.py --project <id> latest mini-prd`. Its
Constraints section is a legitimate architecture-driver source (a
regulatory requirement, a mandate to use existing infrastructure) that
won't appear in FR or NFR. Proceed without it if it doesn't exist.

## Treat supplied requirements as the source of truth — but validate them first

Do not silently change, reinterpret, or discard a requirement. Before
designing anything, check for: contradictions, ambiguity, missing
information, incompatible FR/NFR expectations, unrealistic constraints,
missing architectural drivers, conflicts between the two documents.

**Hard gate.** If a material, unresolved contradiction exists that can't
be resolved without inventing information, stop architecture synthesis
entirely. Set the document's Architecture Status to `BLOCKED` and record,
for each conflict: the specific conflicting requirement IDs, what
conflicts, why it conflicts, the exact clarification required, and which
architectural decisions can't safely be made as a result. Do not invent a
compromise to make the contradiction go away.

```
Architecture Status: BLOCKED

Conflict:
FR-023 requires immediate consistency.
NFR-017 permits asynchronous propagation up to 30 seconds.

Impact:
The consistency model cannot be selected safely.

Required clarification:
Should the affected operation guarantee read-after-write consistency, or
is eventual consistency acceptable?
```

**Non-blocking ambiguity** doesn't stop you — make the smallest reasonable
assumption, document it explicitly (see classification below), and state
its architectural impact and what would change if it turns out to be
wrong. Don't hide an assumption inside confident-sounding prose.

## Facts, assumptions, and decisions — never blur these

Distinguish, in your own reasoning and in what you write:
- **Requirement** — explicitly stated by FR/NFR/Mini-PRD.
- **Derived** — logically follows from stated requirements.
- **Assumption** — introduced because information is missing.
- **Decision** — an architectural choice you're making.
- **Unknown** — genuinely unavailable, needs validation.

Never present an assumption or a decision as if it were a requirement.
Never invent: traffic/user numbers, latency targets, availability
guarantees, capacity figures, infrastructure sizing, cost, vendor
capabilities, benchmarks, performance guarantees, or compliance
obligations. When a current external fact materially affects a decision
(a cloud provider's capability, a database's actual limits, a protocol's
behavior), verify it — use web search rather than relying on memory if
you have that tool available and the fact genuinely matters to the
decision — and cite the source, or state plainly that verification is
required if you can't confirm it.

## Architectural drivers, ranked

Identify the characteristics that materially influence this architecture,
then rank them by business importance, architectural impact, and
difficulty of changing later. Not every NFR deserves equal weight — a
handful of ranked drivers is more useful than an exhaustive equally-
weighted list. See `references/architecture-reasoning.md` for the
FR+NFR → driver → decision → technology chain every consequential
decision should visibly follow — never jump straight from a requirement
to a named technology.

## Architecture style: evaluate the simplest first

Consider styles proportionally to what the requirements actually need:
modular monolith, layered, hexagonal/clean, distributed services,
microservices, event-driven, serverless, hybrid. **Do not default to
microservices or distributed architecture.** Define boundaries on
meaningful factors — business capability, ownership, consistency needs,
change patterns, security boundaries, scaling characteristics — not
because the system happens to contain multiple entities or modules. If
domain complexity genuinely warrants formal domain modeling,
`references/ddd-glossary.md` has optional terminology for that — but
it's a technique to reach for when justified, not a mandatory structure.
Compare alternatives (Section 7) only when more than one style was
genuinely viable; skip the comparison theater when the choice is
clear-cut.

## Data and distributed systems — when relevant

Reason explicitly about data ownership, transactional boundaries,
consistency, concurrency, idempotency, retries, timeouts, ordering,
duplication, partial failure, replication, caching, backpressure, and
recovery **when the system's shape actually raises these questions**. If
the architecture crosses process/service/machine/region/network
boundaries, don't assume a distributed call behaves like a local function
call. If the system is simple and local, don't manufacture distributed-
systems complexity to fill the section — say so and move on. The source
of truth and ownership of every important piece of data must always be
unambiguous, regardless of how simple or complex the rest of the system
is.

## API design — contracts, not implementation

Where architecturally relevant: interface responsibility, major
resources/operations, request/response semantics, authn/authz,
idempotency, versioning, error model, sync vs. async. Focus on the
contract; don't produce implementation code.

## Security, reliability, resilience — proportional to risk

Cover what actually matters for this system's risk profile: authn,
authz, trust boundaries, data protection, abuse prevention on the
security side; timeouts, retries, circuit breaking, graceful degradation
on the resilience side. For every important dependency, say what happens
when it fails. Don't produce a generic checklist with no architectural
relevance to this system — that's padding, not rigor.

## Capacity and scaling — only when scale materially affects the architecture

Use supplied workload data, measured data, or explicit assumptions —
never fabricated numbers. If workload data is unavailable, describe
scaling mechanisms qualitatively rather than inventing false precision:
*"The application is stateless and can scale horizontally; exact
infrastructure capacity should be established through load testing once
workload targets are known."* Introduce partitioning, sharding, multi-
region, or distributed caching only when requirements or evidence justify
them. If a real capacity model is warranted but inputs are missing, mark
`capacity_model.status` as `INCOMPLETE` and list exactly what's missing.

## Technology selection — architecture first, technology follows

Recommend specific technologies only when they materially help the
design. For significant choices: why it fits, real trade-offs,
meaningful alternatives, relevant constraints. Prefer existing
organizational/platform standards when the user has mentioned any. Don't
choose by popularity, and don't invent capabilities, limits, benchmarks,
pricing, or performance characteristics — verify or mark as requiring
verification (see "Facts, assumptions, and decisions" above).

## Architecture decisions — significant ones only

Document only decisions that are genuinely significant or expensive to
reverse. Use the concise four-part ADR format in
`references/adr-format.md` (Context, Decision, Alternatives, Trade-offs)
— don't write an ADR for every implementation detail. Always state
trade-offs explicitly; never describe a decision as having none.

## Completeness Assessment

Exactly one Architecture Status, with exactly this meaning:
- **READY_FOR_IMPLEMENTATION_PLANNING** — requirements are sufficiently
  complete and the architecture is sufficiently defined, with no
  significant open assumptions.
- **READY_WITH_ASSUMPTIONS** — the architecture can proceed, but explicit
  assumptions remain (list them, classified, with impact — see above).
  This is the common case, not a failure state.
- **BLOCKED** — a material, unresolved contradiction prevents a
  trustworthy architecture (see the hard gate above).

Map this to the envelope `status` per `references/pipeline-conventions.md`'s
table (both READY variants → envelope `READY`; `BLOCKED` → envelope
`CONFLICT`, since per this skill's definition `BLOCKED` specifically means
an unresolved contradiction, not just missing information — missing
information alone is an assumption, not a block).

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version architecture-design`.
If it returns a `previous_doc_path`/`previous_data_path`, read both as
your baseline. Change only what the new/changed FR or NFR content
actually affects — preserve ADRs and decisions that remain valid, and add
a new ADR (marking the old one `Superseded by ADR-N`, never silently
rewriting it) if a decision needs to change.

## MVP scope

Read `mvp.number` from both FR and NFR `data.json` — they should match;
if they don't, stop and report which one is behind (NFR hasn't caught up
to FR's latest round yet). Set your own `mvp.number` to match. Design only
for what's in scope now — component/architecture-style boundaries should
be stable across MVPs; a new MVP typically adds detail within an existing
boundary rather than redrawing it. Set `mvp.is_final` to true only when
both inputs' `mvp.is_final` are also true.

## Final self-check before finishing (Architecture Validation, Section 30)

Before writing the Completeness Assessment: does every significant FR/NFR
have an architectural treatment? Is the document internally consistent
(no contradiction between components, data ownership, consistency model,
and ADRs)? Is it technically feasible? Have you avoided unnecessary
distributed-system machinery the requirements don't justify? Are critical
failure scenarios addressed? Can this realistically be operated? Can it
evolve without unnecessary coupling? Does every major decision trace back
to a requirement or driver?

## Human review checkpoint — before writing anything to disk

Draft the complete document **directly in your response**, not to disk
yet. Walk through the architecture style choice and the key ADRs — the
user needs enough to actually evaluate it, not just a "done!" Then ask
something like: *"Here's the architecture: \<style\> because \<driver\>,
with \<N\> key decisions (ADR-1 through ADR-N). Does this work for you —
any constraints I should account for, or anything you'd change — before I
lock this in as v\<version\>?"* Stop and wait for their reply in a new
turn.

If they push back on the style or a decision, revise (superseding an ADR
rather than silently editing it) and ask again. Repeat until the user
explicitly confirms, or explicitly tells you to proceed without further
review. If your status is `BLOCKED`, present the conflict itself for this
checkpoint instead — the question becomes "which side should change, or
how would you like to reconcile this?"

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version architecture-design`
2. Write `<project-root>/architecture-design/v<version>.md` (from
   `templates/architecture-design.md`) and
   `<project-root>/architecture-design/v<version>.data.json` (per
   `schema/architecture-design.schema.json`) — `<project-root>` is the
   `path` from Step 1's `resolve-project` output.
3. Record `inputs_consumed` for both `functional-requirements` and
   `non-functional-requirements` (version + hash from the `check-ready`
   output above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data architecture-design --path <project-root>/architecture-design/v<version>.data.json`
5. Write the envelope to `<project-root>/architecture-design/v<version>.envelope.json`,
   mapping your Architecture Status per the table above, with
   `"next_skill": "mermaid-diagrams"` (set this even on `BLOCKED`/envelope
   `CONFLICT`, since re-running after resolution still leads there).
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/architecture-design/v<version>.envelope.json`
7. Report to the user the version produced, a short summary, the
   Architecture Status and why, and whether `mermaid-js` can now run.

See `examples/url-shortener-architecture.md` for a fully worked document
(including a genuine "Not Applicable" section and an assumption-driven
`READY_WITH_ASSUMPTIONS` status) plus its matching `data.json`.
