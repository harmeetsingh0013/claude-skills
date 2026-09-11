# System Architecture & Design Document

> **Adaptive depth, not a form to fill mechanically.** The section list below
> is canonical — don't drop or reorder sections — but depth is not. A
> section should be detailed when architecturally important, concise when
> moderately relevant, and marked **"Not Applicable"** (with a one-line
> reason) when genuinely irrelevant to this system. Never pad a section
> with generic theory just to make the document look complete. A simple
> system should produce a simple, concise document; a complex distributed
> system warrants deeper analysis where the complexity actually is.

Architecture Status: READY_FOR_IMPLEMENTATION_PLANNING / READY_WITH_ASSUMPTIONS / BLOCKED

Document Version: [X.Y]

---

## 1. Executive Summary

Purpose, business context, proposed architecture, major architectural
characteristics, major decisions, major risks, architecture status.

## 2. Input Documents

### Functional Requirements
Version: | Validation: PASS/FAIL

### Non-Functional Requirements
Version: | Validation: PASS/FAIL

### Other Inputs
(Mini-PRD constraints, existing-system context, etc. — only if relevant)

## 3. Requirements Validation

### Requirement Integrity
### Cross-Document Validation
### Conflicts
Use the hard-blocking format (see SKILL.md) for any material, unresolved
contradiction. If none: "No material conflicts identified."

### Missing Information
### Assumptions
Each assumption: statement, classification (ASSUMPTION / DERIVED /
UNKNOWN), architectural impact, and what would change if it's wrong.

### Architecture Status
READY_FOR_IMPLEMENTATION_PLANNING / READY_WITH_ASSUMPTIONS / BLOCKED

## 4. Architectural Drivers

Ranked list — business importance, architectural impact, difficulty of
changing later. Not every NFR is equally important; rank them.

## 5. System Context

External actors, external dependencies, system boundary. Text/structured
description is fine — no diagram is produced at this stage (see note
below).

## 6. Architecture Overview

Architectural style in plain terms, logical structure, why this shape
fits the drivers above. Domain/component boundaries can be described here
based on business capability, ownership, consistency needs, change
patterns — without requiring a full separate domain-modeling exercise
unless the system's complexity actually warrants one.

## 7. Architecture Alternatives

Only when more than one style was genuinely viable. Each alternative:
advantages, disadvantages, assessment (selected/rejected and why). Skip
or keep brief if the choice was clear-cut.

## 8. Architecture Decisions

### ADR-001 — [Decision Title]
Status: | Context: | Decision: | Alternatives: | Trade-offs:

(repeat per significant decision — see references/adr-format.md. Don't
write an ADR for every implementation detail.)

## 9. Component / Service Architecture

Per component/service: responsibility, owned data, key dependencies.
Avoid creating components merely to make the document look sophisticated.

## 10. Request Flows

The most architecturally significant flows only — described as ordered
steps or a sequence in text. Not every possible flow needs one.

## 11. Data Architecture

Data ownership, authoritative sources, persistence model, replication,
retention — as relevant.

## 12. Data Model

Key entities/tables and their important fields/constraints, at the level
that clarifies ownership and consistency — not a full schema unless
warranted.

## 13. API Design

Only where architecturally relevant: interface responsibility, major
resources/operations, request/response semantics, authn/authz,
idempotency, versioning, error model. Focus on contracts, not
implementation.

## 14. Caching Architecture

What's cached, why, invalidation, failure behavior — or "Not Applicable"
if the system doesn't need caching.

## 15. Messaging / Event Architecture

Events/commands, delivery semantics, ordering, idempotency — or "Not
Applicable" if the system is fully synchronous.

## 16. Consistency & Concurrency

Where strong consistency is required and why; where eventual consistency
is acceptable and why. Concurrency handling for anything with real
contention risk.

## 17. Security Architecture

Proportional to risk: authn, authz, trust boundaries, data protection,
abuse prevention — the parts that actually matter for this system, not a
generic checklist.

## 18. Scalability Architecture

Only with real analysis if scale materially affects the architecture;
otherwise state the scaling mechanism qualitatively (e.g. "stateless,
scales horizontally; exact capacity requires load testing once workload
targets are known").

## 19. Availability Architecture

Redundancy and failure-domain reasoning proportional to the stated
availability target (if any).

## 20. Reliability & Resilience

Timeouts, retries, circuit breaking, graceful degradation — where a
dependency failure actually needs a defined behavior.

## 21. Disaster Recovery

RTO/RPO if known; explicitly UNKNOWN if not, with what's needed to define
them.

## 22. Observability

What must be logged/measured/traced/alerted — the parts that matter for
this system's actual failure modes and business questions, not a generic
observability checklist.

## 23. Deployment Architecture

Runtime, redundancy/zone strategy, deployment approach — as relevant to
the availability/scale drivers.

## 24. Technology Selection

Only for choices that materially matter. Fit, trade-offs, alternatives.
Verify current external facts (capabilities, limits) rather than
asserting them from memory when they matter to the decision — cite the
source or mark "verification required."

## 25. Technology Alternatives

Table: capability | selected | alternative(s) | reason. Only for
significant choices.

## 26. Architecture Trade-offs

Explicit tensions (consistency vs availability, latency vs durability,
simplicity vs scalability, etc.) — never claim the architecture has no
trade-offs.

## 27. Failure Mode Analysis

Table: failure mode | impact | mitigation — for the failure modes that
are actually plausible and consequential for this system.

## 28. Capacity / Scaling Analysis

Only if scale materially affects the architecture. Use supplied numbers
and explicit formulas; never fabricate. If inputs are missing: "Capacity
Status: INCOMPLETE" plus exactly what's missing.

## 29. Requirements Traceability

Table: requirement ID | architectural response. Flag any requirement
with no architectural treatment.

## 30. Architecture Validation

Final self-check: requirement coverage, internal consistency, feasibility,
complexity (no unjustified distributed-system machinery), failure
handling, security, operability, evolvability, traceability.

## 31. Risks

Table: ID | risk | severity | mitigation.

## 32. Open Questions

Numbered list — genuinely open, not-yet-blocking questions.

## 33. Future Evolution

What would change the architecture if it happened (scale growth,
geographic expansion, new consistency requirement) — evolutionary paths,
not speculative work to do now.

## MVP Scope

MVP number (matches the FR/NFR documents this design was derived from):
Is this the final MVP?

Design only for this MVP's FR/NFR scope. Bounded contexts / component
boundaries (section 6/9) are usually stable across MVPs — a new MVP
typically adds detail within an existing boundary rather than redrawing
boundaries entirely.

---

Appendix A — Source & Context Notes

Architectural assumptions and their basis; what's known vs. what's
inferred; known uncertainty and its impact on the document's confidence
level.

---

**Note on diagrams:** this document does not include a diagram
specification. Diagram generation is a separate skill (`mermaid-js`),
which derives what to draw directly from this document's structured
content (System Context, Architecture Overview, Component Architecture,
Request Flows, Data Model, Deployment Architecture) — you don't need to
tell it what diagrams to produce.
