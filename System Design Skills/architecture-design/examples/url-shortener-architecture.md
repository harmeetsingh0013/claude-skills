# Worked example: Architecture Design — TeamLink (continued)

Derived from functional-requirements v1.0 and non-functional-requirements
v1.0 (see the FR and NFR examples). This example deliberately shows
**adaptive depth**: TeamLink is a small-team product with modest scale, so
several sections stay short or are marked Not Applicable rather than
padded out — contrast this with a system where distributed-systems
rigor, capacity modeling, or multi-region DR would actually be warranted.

## Excerpt of the .md document

```markdown
# System Architecture & Design Document

Architecture Status: READY_WITH_ASSUMPTIONS
Document Version: 1.0

## 1. Executive Summary

TeamLink is a small-team URL shortener. Redirect traffic will exceed
link-creation traffic, but at a scale (a handful of teams, low hundreds of
members) that does not justify distributed infrastructure. The proposed
architecture is a single stateless service backed by a relational
database, with click analytics published asynchronously so they never add
latency to the redirect path. No caching, message broker, or
microservices are introduced — none are justified by the stated scale.

## 3. Requirements Validation

### Conflicts
No material conflicts identified between FR-001..009 and NFR-001..002.

### Assumptions
- **A-1** (ASSUMPTION): Team count and redirect volume remain small enough
  that a single database instance handles both reads and writes without
  read scaling. Architectural impact: no read replica or cache is
  introduced in this version. If false: read scaling (a cache or replica)
  becomes a near-term architectural driver, not a future one.
- **A-2** (UNKNOWN): Exact expected redirect volume was not specified in
  NFR. Architectural impact: Section 28 (Capacity/Scaling) is marked
  INCOMPLETE rather than estimated.

### Architecture Status
READY_WITH_ASSUMPTIONS

## 4. Architectural Drivers

1. Redirect correctness (FR-004) — highest business importance; a wrong
   redirect is a critical failure.
2. Redirect latency not degraded by analytics (NFR-002) — directly shapes
   the async-analytics decision.
3. Team-scoped authorization (FR-006/007) — affects data model and API
   design, moderate difficulty to change later.

## 6. Architecture Overview

A single stateless service (modular internally: link management, redirect
resolution, team/access, analytics ingestion) backed by one relational
database. No service decomposition — the scale described in FR/NFR does
not justify the operational cost of separate deployables.

## 8. Architecture Decisions

### ADR-003 — Publish click events asynchronously
**Status:** Accepted
**Context:** FR-005 requires recording every click; NFR-002 requires that
recording not add redirect latency.
**Decision:** The redirect handler publishes a click event to a queue and
returns immediately; a separate consumer writes it to storage.
**Alternatives:** Synchronous write during redirect — rejected, directly
violates NFR-002.
**Trade-offs:** Click counts lag redirects by the queue-processing delay;
acceptable since no NFR requires real-time analytics.

## 14. Caching Architecture

Not Applicable — read volume at the stated scale does not justify a
cache; the database serves reads directly. Revisit if A-1 proves false.

## 21. Disaster Recovery

RTO/RPO: UNKNOWN — not specified in NFR. Required before this can move to
READY_FOR_IMPLEMENTATION_PLANNING: an explicit recovery target from the
product owner.

## 28. Capacity / Scaling Analysis

Capacity Status: INCOMPLETE

Missing:
- expected redirects/day
- expected concurrent teams/members
- expected data growth rate

Qualitative note: the application tier is stateless and can scale
horizontally if needed; the database is the only stateful component and
has no scaling design yet because no evidence currently requires one.

## Completeness Assessment

Architecture status:
READY_WITH_ASSUMPTIONS
```

(trimmed for length — sections 2, 5, 7, 9-13, 15-20, 22-27, 29-33 and
Appendix A follow the same adaptive-depth pattern: real content where it
matters — e.g. Section 16 Consistency & Concurrency has real substance
because short-code uniqueness is a genuine correctness requirement —
concise or "Not Applicable" elsewhere.)

## The matching data.json (excerpt)

```json
{
  "document_id": "ARCH-TEAMLINK-001",
  "product": "TeamLink URL Shortener",
  "version": "1.0",
  "created": "2026-01-17",
  "input_documents": {
    "functional_requirements": {"version": "1.0", "validation": "PASS"},
    "non_functional_requirements": {"version": "1.0", "validation": "PASS"}
  },
  "status": "READY_WITH_ASSUMPTIONS",
  "mvp": {"number": 1, "is_final": false},
  "assumptions": [
    {
      "id": "A-1",
      "statement": "Team count and redirect volume remain small enough that a single database instance handles both reads and writes without read scaling.",
      "classification": "ASSUMPTION",
      "architectural_impact": "No read replica or cache is introduced in this version.",
      "if_false": "Read scaling becomes a near-term architectural driver, not a future one."
    },
    {
      "id": "A-2",
      "statement": "Exact expected redirect volume was not specified in NFR.",
      "classification": "UNKNOWN",
      "architectural_impact": "Section 28 is marked INCOMPLETE rather than estimated.",
      "if_false": "N/A - this is a data gap, not a reversible assumption."
    }
  ],
  "architectural_drivers": [
    {"rank": 1, "driver": "Redirect correctness", "reason": "FR-004; a wrong redirect is a critical failure."},
    {"rank": 2, "driver": "Redirect latency isolated from analytics", "reason": "NFR-002 directly shapes the async-analytics decision."},
    {"rank": 3, "driver": "Team-scoped authorization", "reason": "FR-006/007; affects data model and API design."}
  ],
  "architecture_style": {
    "selected": "Single stateless service, modular internally (no service decomposition)",
    "rationale": "Stated scale (a handful of teams, low hundreds of members) does not justify the operational cost of separate deployables.",
    "alternatives_considered": [
      {
        "name": "Microservices (separate link/redirect/analytics services)",
        "advantages": ["Independent scaling", "Failure isolation"],
        "disadvantages": ["Network calls", "Distributed operational overhead not justified at this scale"],
        "assessment": "Rejected - not justified by current requirements."
      }
    ]
  },
  "components": [
    {"name": "Redirect Handler", "responsibility": "Resolves short codes and returns redirects; publishes click events without waiting on them.", "owned_data": "None (reads link data)"},
    {"name": "Click Consumer", "responsibility": "Reads click events off the queue and writes them to durable storage.", "owned_data": "Click event log"}
  ],
  "adrs": [
    {
      "id": "ADR-003",
      "title": "Publish click events asynchronously",
      "status": "Accepted",
      "context": "FR-005 requires recording every click; NFR-002 requires that recording not add redirect latency.",
      "decision": "The redirect handler publishes a click event to a queue and returns immediately; a separate consumer writes it to storage.",
      "alternatives": ["Synchronous write during redirect - rejected, directly violates NFR-002."],
      "trade_offs": "Click counts lag redirects by the queue-processing delay; acceptable since no NFR requires real-time analytics.",
      "driven_by": ["FR-005", "NFR-002"]
    }
  ],
  "consistency_model": {
    "strong_consistency_areas": ["Short-code uniqueness (FR-003)", "Custom alias uniqueness"],
    "eventual_consistency_areas": ["Click analytics (FR-006/007)"]
  },
  "capacity_model": {
    "status": "INCOMPLETE",
    "missing_inputs": ["expected redirects/day", "expected concurrent teams/members", "expected data growth rate"],
    "formulas": []
  },
  "trade_offs": [
    {"tension": "Synchronous simplicity vs. asynchronous decoupling", "resolution": "Chose async for click events specifically because NFR-002 makes redirect latency non-negotiable; everything else stays synchronous for simplicity."}
  ],
  "risks": [
    {"id": "R-001", "risk": "Queue outage silently drops click analytics (not redirects).", "severity": "Low", "mitigation": "Monitor queue health; acceptable per NFR-002 since analytics is not redirect-critical."}
  ],
  "open_questions": [
    "What is the target RTO/RPO for disaster recovery?",
    "What is the expected redirect volume, for capacity planning?"
  ],
  "traceability": [
    {"requirement_id": "FR-005", "architectural_response": "Click Consumer + ADR-003"},
    {"requirement_id": "NFR-002", "architectural_response": "ADR-003 (async publication)"}
  ],
  "not_applicable_sections": [
    {"section": "14. Caching Architecture", "reason": "Read volume at stated scale does not justify a cache."},
    {"section": "15. Messaging / Event Architecture", "reason": "Only the single click-event queue exists; covered under ADR-003, no broader event architecture needed."}
  ]
}
```

Notice what's absent: no diagram specification anywhere in this document
— that's mermaid-js's job now, working directly from this content (it
would derive a component diagram from `components`, and a request-flow
diagram from the redirect sequence described in Section 10, without
being told to).
