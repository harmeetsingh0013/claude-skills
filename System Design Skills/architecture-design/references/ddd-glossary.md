# Domain-Driven Design: glossary and heuristics

Quick reference for the terms and patterns architecture-design uses.
This is a lookup, not a tutorial — it's here so terminology stays
consistent across a document, not to teach DDD from scratch.

## Strategic design (the big picture)

**Ubiquitous Language** — a vocabulary shared between the domain experts
(the FR/NFR documents, effectively) and the design, used consistently
everywhere: in conversation, in the documents, and eventually in code. If
a term means something different in two parts of the system (e.g. "Team"
means a billing unit in one place and a permissions group in another),
that's usually a sign they belong in different bounded contexts, not that
someone picked the wrong word.

**Bounded Context** — an explicit boundary within which a particular
domain model (and its ubiquitous language) applies consistently. This is
the primary strategic design tool, and in this pipeline, **a bounded
context is what becomes a module** — the unit a future implementation
task-breakdown works from. Heuristics for finding boundaries:
- A capability grouping in the FR document (its `### <Capability>`
  headings) is often already a good starting hint.
- Different NFR profiles are a strong signal — if one area needs strict
  consistency and low latency while another can tolerate eventual
  consistency and higher latency (the classic redirect-vs-analytics
  split), that's usually two contexts, not one.
- The same word meaning different things in different areas (see
  Ubiquitous Language above).
- Natural ownership boundaries — if you can imagine two different teams
  owning two different parts of the system independently, that's a hint.

**Context Map** — the relationships between bounded contexts. Every
relationship should use one of these patterns, with a stated rationale —
don't leave a relationship unlabeled or invent a pattern name:
- **Partnership** — two contexts succeed or fail together; teams
  coordinate closely.
- **Shared Kernel** — two contexts explicitly share a subset of the
  model; changes to the shared part need both sides' agreement.
- **Customer-Supplier** — the supplier context's model influences the
  customer context, but not vice versa; supplier prioritizes the
  customer's needs.
- **Conformist** — the downstream context just accepts the upstream
  model as-is, with no translation, because it has no leverage or reason
  to negotiate.
- **Anticorruption Layer (ACL)** — the downstream context translates the
  upstream model into its own terms at the boundary, protecting its own
  model from the upstream's design.
- **Open Host Service** — a context exposes a well-defined service/API
  for others to integrate with, rather than one-off integrations per
  consumer.
- **Published Language** — integration happens through a well-documented
  shared format (often paired with Open Host Service) — domain events are
  a common published language.
- **Separate Ways** — no meaningful integration; duplicating a little
  logic is cheaper than coordinating.

## Tactical design (inside one bounded context)

**Aggregate** — a cluster of entities/value objects treated as a single
unit for data changes, with one **Aggregate Root** as its only entry
point. The aggregate boundary is also the **transactional consistency
boundary** — invariants inside an aggregate must hold after every
transaction; consistency *between* aggregates is eventual, coordinated
through domain events, not a bigger transaction. This is the direct link
to non-functional-requirements' consistency/concurrency NFRs.

**Entity** — has a distinct identity that persists over time even as its
attributes change (e.g. a specific Link, identified by its short code,
regardless of how its metadata changes).

**Value Object** — defined entirely by its attributes, no identity of its
own, usually immutable (e.g. a date range, a money amount, a geographic
region).

**Domain Event** — something that happened in the domain that other parts
of the system (often other bounded contexts) care about (e.g.
`LinkClicked`, `TeamMemberRemoved`). This is the usual mechanism for
integration between bounded contexts when the context map calls for
Published Language / Open Host Service rather than a direct synchronous
call — and it's often what an NFR-driven decoupling decision (see
`references/architecture-reasoning.md`) turns into concretely.

**Domain Service** — an operation that doesn't naturally belong to one
entity or value object (spans several, or represents a domain concept
that's inherently a verb, not a noun). Distinct from an **Application
Service** (orchestrates a use case: load an aggregate, call domain logic,
save it, publish events — no business rules of its own) and
**Infrastructure** (technical concerns: persistence, messaging,
external-system adapters).

## What this pipeline does and doesn't do with these concepts

Identify bounded contexts, name their aggregates/entities/value objects,
state aggregate invariants in prose, and name domain events — this is
design, and it's this skill's job. Writing actual class definitions,
method signatures, interface code, or database DDL is implementation —
that's out of scope here, same as it's out of scope for every other stage
of this pipeline. A future task-breakdown step (outside this pipeline)
is what turns a well-defined module boundary into actual work items and
code.
