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

## 4. Architectural Drivers

The FRs/NFRs that most shape this design, and the driver they produce.
Use the FR+NFR -> driver -> decision -> technology-evaluation ->
technology-decision chain (see references/architecture-reasoning.md) —
don't jump straight from a requirement to a named technology.

## 5. System Context

## 6. Architecture Overview

## 7. Architecture Alternatives

## 8. Architecture Decisions

### ADR-001
### ADR-002
...
(see references/adr-format.md for the format of each entry)

## 9. Component / Service Architecture

## 10. Request Flows

## 11. Data Architecture

## 12. Data Model

## 13. API Design

## 14. Caching Architecture

## 15. Messaging / Event Architecture

## 16. Consistency & Concurrency

## 17. Security Architecture

## 18. Scalability Architecture

## 19. Availability Architecture

## 20. Reliability & Resilience

## 21. Disaster Recovery

## 22. Observability

## 23. Deployment Architecture

## 24. Technology Selection

## 25. Technology Alternatives

## 26. Architecture Trade-offs

## 27. Failure Mode Analysis

## 28. Capacity / Scaling Analysis

## 29. Requirements Traceability

Table: FR-N/NFR-N -> section(s) of this document that address it. Flag any
requirement that isn't addressed anywhere.

## 30. Architecture Validation

## 31. Risks

## 32. Open Questions

## 33. Future Evolution

## 34. Mermaid Diagram Specification

List each diagram mermaid-js should produce: name, type (one of
system-context / container-architecture / request-flow / data-flow /
sequence-diagram / deployment-architecture / entity-relationship /
state-diagram), and what it must show. Only list diagrams the design
actually warrants — not one of every type by default.

## MVP Scope

MVP number (matches the FR/NFR documents this design was derived from):
Is this the final MVP?

Design only for this MVP's FR/NFR scope — don't speculatively build
infrastructure for deferred requirements that haven't been approved yet.
Carry forward ADRs/components from earlier MVPs unchanged unless this
MVP's new requirements actually affect them.

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
