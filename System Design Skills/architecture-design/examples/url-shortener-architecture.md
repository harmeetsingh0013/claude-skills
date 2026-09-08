# Worked example: Architecture Design — TeamLink (continued)

Derived from functional-requirements v1.0 and non-functional-requirements
v1.0 (see the FR and NFR examples). No contradictions were found between
them, so this proceeds to a real design rather than a conflict report.

## Excerpt: Section 4 (Architectural Drivers) through the ADR

```markdown
## 4. Architectural Drivers

FR-005 (record every click) combined with NFR-002 (click recording must
not add redirect latency) produces a clear driver: analytics must be
decoupled from redirect processing. See references/architecture-reasoning.md
for why this is written as a chain rather than jumping straight to a
technology.

## 8. Architecture Decisions

### ADR-003: Publish click events asynchronously via a managed queue

**Status:** Accepted
**Driven by:** FR-005, NFR-002

**Context:** Redirects (FR-004) must stay under 100ms p99 (NFR-001), and
click recording (FR-005) must not add to that latency (NFR-002).

**Decision:** The redirect handler publishes a click event to a queue and
returns immediately; a separate consumer writes the event to storage.

**Alternatives considered:**
- Synchronous write to the database during the redirect — rejected:
  directly violates NFR-002.
- In-memory buffer flushed periodically — rejected: risks event loss on
  process restart, which a small-team analytics feature can tolerate less
  than the operational simplicity gained.
- Managed queue (SQS) vs. self-hosted Kafka — SQS chosen: this product's
  scale (small teams, not high-throughput analytics) doesn't justify
  Kafka's operational overhead; SQS meets the durability need with far
  less to operate.

**Consequences:** Click analytics (FR-006/FR-007) has slight (queue-
processing) latency before a click appears in reports — acceptable since
no NFR requires real-time analytics.
```

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
  "status": "READY_FOR_MERMAID",
  "conflicts": [],
  "adrs": [
    {
      "id": "ADR-003",
      "title": "Publish click events asynchronously via a managed queue",
      "status": "Accepted",
      "driven_by": ["FR-005", "NFR-002"]
    }
  ],
  "components": [
    {"name": "Redirect Service", "responsibility": "Resolves short codes and returns redirects; publishes click events without waiting on them."},
    {"name": "Click Consumer", "responsibility": "Reads click events off the queue and writes them to durable storage."}
  ],
  "diagram_specifications": [
    {
      "name": "request-flow",
      "type": "sequence-diagram",
      "shows": "Redirect path from visitor click through async click-event publication."
    },
    {
      "name": "entity-relationship",
      "type": "entity-relationship",
      "shows": "Team/Member/Link/ClickEvent relationships."
    }
  ],
  "risks": [
    "Queue outage would silently drop click analytics (not redirects) — acceptable per NFR-002 but should be monitored."
  ],
  "open_questions": [],
  "traceability": [
    {"requirement_id": "FR-005", "sections": ["4", "8", "9"]},
    {"requirement_id": "NFR-002", "sections": ["4", "8"]}
  ]
}
```

Notice this document's `diagram_specifications` list has exactly two
entries — not one of every possible diagram type. mermaid-js will produce
exactly those two, as shown in its own worked example.
