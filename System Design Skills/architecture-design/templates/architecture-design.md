# System Architecture & Design Document

## 1. Executive Summary

## 2. Input Documents

### Functional Requirements
Version:
Validation: PASS/FAIL

### Non-Functional Requirements
Version:
Validation: PASS/FAIL

## 3. Requirements Validation

### Conflicts
Contradictions found between the FR and NFR documents. If any exist, this
document's Completeness Assessment status must be CONFLICT, not
READY_FOR_MERMAID — see references/pipeline-conventions.md.

### Missing Information
### Assumptions

## 4. Ubiquitous Language

Table: Term | Definition | Bounded Context (if the term is specific to
one). Draw terms from the FR/NFR documents' own vocabulary — don't invent
new names for things they already named. If the same word means different
things in different areas, that's usually a sign of separate bounded
contexts (see section 5), and each meaning gets its own row here.

| Term | Definition | Bounded Context |
|------|------------|------------------|

## 5. Bounded Contexts (Strategic Design)

Identify the bounded contexts this system decomposes into. See
`references/ddd-glossary.md` for the heuristics (capability groupings,
differing NFR profiles, vocabulary splits, ownership boundaries). Each
bounded context named here is a natural unit for future implementation
planning, though breaking that down into modules/tasks is a separate
skill's job, not this document's.

### BC-01: <name>
**Responsibility:**
**Core aggregates:** (named here, detailed in section 8)
**Related requirements:** FR-N, NFR-N, ...

### BC-02: <name>
...

## 6. Context Map (Strategic Design)

Every relationship between two bounded contexts, using one of the
patterns in `references/ddd-glossary.md` (Partnership, Shared Kernel,
Customer-Supplier, Conformist, Anticorruption Layer, Open Host Service,
Published Language, Separate Ways) — never leave a relationship unlabeled.

| From | To | Relationship | Rationale |
|------|-----|--------------|-----------|

## 7. Architectural Drivers

The FRs/NFRs that most shape this design, and the driver they produce.
Use the FR+NFR -> driver -> decision -> technology-evaluation ->
technology-decision chain (see references/architecture-reasoning.md) —
don't jump straight from a requirement to a named technology. Note which
architectural drivers directly motivated a bounded context split in
section 5 (e.g. an NFR forcing a consistency/availability split is
usually also the reason two things became separate contexts, not just
separate technologies).

## 8. Tactical Design

Per bounded context: its aggregates (aggregate root, the entities/value
objects it contains, and its invariants — what must always hold true
after a transaction), and the domain events it publishes or consumes.
Prose descriptions only — no class definitions, method signatures, or
code; see `references/ddd-glossary.md` for what belongs here vs. what's
implementation.

### BC-01: <name>

**Aggregate: <name>**
- Aggregate root:
- Entities:
- Value objects:
- Invariants:

**Domain events published:**
- `<EventName>` — when it fires, what it carries, who's known to consume it

**Domain events consumed:**
- `<EventName>` from BC-0N — how this context reacts to it

### BC-02: <name>
...

## 9. Architecture Decisions

### ADR-001
### ADR-002
...
(see references/adr-format.md for the format of each entry; reference the
bounded context(s) an ADR affects where relevant)

## 10. Component / Service Architecture

State explicitly whether each component maps 1:1 to a bounded context, or
whether multiple contexts are pragmatically combined into one deployable
component (and why — e.g. low individual traffic doesn't justify separate
services yet). A component silently crossing bounded-context lines without
a stated reason is worth a second look.

## 11. Request Flows

## 12. Data Architecture

Note where a bounded context owns its own data store vs. shares one, and
why — sharing storage across bounded contexts is usually a sign of a
Shared Kernel relationship (see section 6) and should be named as such.

## 13. Data Model

## 14. API Design

## 15. Caching Architecture

## 16. Messaging / Event Architecture

Should directly implement the domain events named in section 8 and the
Published Language / Open Host Service relationships named in section 6
— this section is where those become a concrete technology choice.

## 17. Consistency & Concurrency

State the consistency boundary explicitly in terms of aggregates (section
8): strong consistency within an aggregate, eventual consistency across
aggregates and across bounded contexts, coordinated via domain events.

## 18. Security Architecture

## 19. Scalability Architecture

## 20. Availability Architecture

## 21. Reliability & Resilience

## 22. Disaster Recovery

## 23. Observability

## 24. Deployment Architecture

## 25. Technology Selection

## 26. Technology Alternatives

## 27. Architecture Trade-offs

## 28. Failure Mode Analysis

## 29. Capacity / Scaling Analysis

## 30. Requirements Traceability

Table: FR-N/NFR-N -> section(s) of this document that address it. Flag any
requirement that isn't addressed anywhere.

## 31. Architecture Validation

## 32. Risks

## 33. Open Questions

## 34. Future Evolution

## 35. Mermaid Diagram Specification

List each diagram mermaid-js should produce: name, type (one of
system-context / container-architecture / request-flow / data-flow /
sequence-diagram / deployment-architecture / entity-relationship /
state-diagram / context-map), and what it must show. Only list diagrams
the design actually warrants — not one of every type by default. A
context-map diagram (section 6) is usually worth including once there's
more than one bounded context.

## MVP Scope

MVP number (matches the FR/NFR documents this design was derived from):
Is this the final MVP?

Design only for this MVP's FR/NFR scope — don't speculatively build
infrastructure for deferred requirements that haven't been approved yet.
Carry forward ADRs/components from earlier MVPs unchanged unless this
MVP's new requirements actually affect them. Bounded contexts (section 5)
are usually stable across MVPs — a new MVP typically adds aggregates or
tactical detail within an existing context rather than redrawing context
boundaries; if a genuinely new problem area appears, a new bounded context
is fine, but don't reshuffle existing ones without a real reason.

## Completeness Assessment

Architecture status:
READY_FOR_MERMAID

<or>

Architecture status:
BLOCKED

Blocking issues:
- ...

<or, if section 3 found contradictions>

Architecture status:
CONFLICT

Conflicts detected:
- CONFLICT_DETECTED: FR-N says ... while NFR-N says ...
