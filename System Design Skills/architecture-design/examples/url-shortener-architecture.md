# Worked example: Architecture Design — TeamLink (continued)

Derived from functional-requirements v1.0 and non-functional-requirements
v1.0 (see the FR and NFR examples). No contradictions were found between
them, so this proceeds to a real design rather than a conflict report.

## Excerpt: Sections 4-9 (Ubiquitous Language through the ADR)

```markdown
## 4. Ubiquitous Language

| Term | Definition | Bounded Context |
|------|------------|------------------|
| Link | A shortened URL mapping a code to a destination URL | Link Management |
| Short Code | The unique per-team identifier a Link resolves from | Link Management |
| Click | A single instance of a visitor following a Link | Analytics |
| Team | The billing/permissions unit that owns Links and Members | Team & Access |
| Member | A user belonging to exactly one Team | Team & Access |

## 5. Bounded Contexts (Strategic Design)

### BC-01: Link Management
**Responsibility:** Owns creation, uniqueness, and resolution of shortened
links.
**Core aggregates:** Link
**Related requirements:** FR-001, FR-002, FR-003, FR-004

### BC-02: Analytics
**Responsibility:** Owns recording and reporting of click activity,
independent of the redirect path's latency budget.
**Core aggregates:** ClickLog
**Related requirements:** FR-005, FR-006, FR-007, NFR-001, NFR-002

### BC-03: Team & Access
**Responsibility:** Owns team membership, roles, and authorization
decisions consumed by the other two contexts.
**Core aggregates:** Team
**Related requirements:** FR-008, FR-009

## 6. Context Map (Strategic Design)

| From | To | Relationship | Rationale |
|------|-----|--------------|-----------|
| Team & Access | Link Management | Customer-Supplier | Link Management needs valid team/member context to authorize link creation; Team & Access's model takes priority since it's the source of truth for identity. |
| Link Management | Analytics | Published Language | Link Management publishes `LinkClicked` as a domain event; Analytics consumes it asynchronously. This is the concrete mechanism behind ADR-003 below — decoupling driven by NFR-002, not an arbitrary choice. |

## 7. Architectural Drivers

FR-005 (record every click) combined with NFR-002 (click recording must
not add redirect latency) produces a clear driver: analytics must be
decoupled from redirect processing. This driver is *why* Analytics is a
separate bounded context from Link Management (section 5), not just a
separate technology choice — see references/architecture-reasoning.md for
the full FR+NFR -> driver -> decision -> technology chain.

## 8. Tactical Design

### BC-01: Link Management

**Aggregate: Link**
- Aggregate root: Link
- Entities: (none beyond the root)
- Value objects: ShortCode, DestinationUrl
- Invariants: ShortCode is unique within the owning Team; DestinationUrl
  must be a well-formed URL.

**Domain events published:**
- `LinkCreated` — carries link ID, team ID, short code; no known
  consumers yet in this MVP.
- `LinkClicked` — carries link ID, timestamp, referrer/location signal;
  consumed by Analytics (BC-02).

### BC-02: Analytics

**Aggregate: ClickLog**
- Aggregate root: ClickLog
- Entities: ClickEntry
- Value objects: (none beyond entry fields)
- Invariants: A ClickEntry always references a Link ID that existed at
  click time (validated at consumption, not via a foreign-key join across
  contexts).

**Domain events consumed:**
- `LinkClicked` from BC-01 — appends a ClickEntry to the relevant
  ClickLog.

## 9. Architecture Decisions

### ADR-003: Publish click events asynchronously via a managed queue

**Status:** Accepted
**Driven by:** FR-005, NFR-002
**Bounded contexts affected:** BC-01 (Link Management, publisher), BC-02
(Analytics, consumer)

**Context:** Redirects (FR-004) must stay under 100ms p99 (NFR-001), and
click recording (FR-005) must not add to that latency (NFR-002).

**Decision:** The redirect handler (BC-01) publishes a `LinkClicked`
domain event to a queue and returns immediately; a separate consumer in
BC-02 writes the event to the ClickLog.

**Alternatives considered:**
- Synchronous write to the database during the redirect — rejected:
  directly violates NFR-002, and would collapse the BC-01/BC-02 boundary
  into a single transaction, defeating the point of separating them.
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

## Excerpt: Section 35 (Module & Task Breakdown Map)

```markdown
## 35. Module & Task Breakdown Map

| Module (Bounded Context) | Depends On | Suggested Task Granularity | MVP Alignment |
|---------------------------|------------|------------------------------|-----------------|
| BC-03 Team & Access | (none) | schema/migration; aggregate + domain logic; application service; API endpoint(s) | 1 |
| BC-01 Link Management | BC-03 | schema/migration; aggregate + domain logic; application service; API endpoint(s); event publisher | 1 |
| BC-02 Analytics | BC-01 | schema/migration; aggregate + domain logic; event consumer; API endpoint(s) for reporting | 1 |

Team & Access has no dependencies, so it's the natural place for a future
implementation effort to start — this table doesn't sequence the work
itself, but the dependency column is what a task-breakdown step would use
to do that.
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
  "mvp": {"number": 1, "is_final": false},
  "conflicts": [],
  "ubiquitous_language": [
    {"term": "Link", "definition": "A shortened URL mapping a code to a destination URL", "bounded_context": "BC-01"},
    {"term": "Click", "definition": "A single instance of a visitor following a Link", "bounded_context": "BC-02"}
  ],
  "bounded_contexts": [
    {
      "id": "BC-01",
      "name": "Link Management",
      "responsibility": "Owns creation, uniqueness, and resolution of shortened links.",
      "aggregates": ["Link"],
      "related_requirements": ["FR-001", "FR-002", "FR-003", "FR-004"]
    },
    {
      "id": "BC-02",
      "name": "Analytics",
      "responsibility": "Owns recording and reporting of click activity, independent of the redirect path's latency budget.",
      "aggregates": ["ClickLog"],
      "related_requirements": ["FR-005", "FR-006", "FR-007", "NFR-001", "NFR-002"]
    },
    {
      "id": "BC-03",
      "name": "Team & Access",
      "responsibility": "Owns team membership, roles, and authorization decisions.",
      "aggregates": ["Team"],
      "related_requirements": ["FR-008", "FR-009"]
    }
  ],
  "context_map": [
    {"from": "BC-03", "to": "BC-01", "relationship": "Customer-Supplier", "rationale": "Link Management needs valid team/member context to authorize link creation."},
    {"from": "BC-01", "to": "BC-02", "relationship": "Published Language", "rationale": "Decoupling driven by NFR-002; LinkClicked is the integration contract."}
  ],
  "domain_events": [
    {"name": "LinkCreated", "bounded_context": "BC-01", "consumed_by": []},
    {"name": "LinkClicked", "bounded_context": "BC-01", "consumed_by": ["BC-02"]}
  ],
  "adrs": [
    {
      "id": "ADR-003",
      "title": "Publish click events asynchronously via a managed queue",
      "status": "Accepted",
      "driven_by": ["FR-005", "NFR-002"]
    }
  ],
  "components": [
    {"name": "Redirect Service", "responsibility": "Resolves short codes and returns redirects; publishes click events without waiting on them.", "bounded_context": "BC-01"},
    {"name": "Click Consumer", "responsibility": "Reads click events off the queue and writes them to durable storage.", "bounded_context": "BC-02"}
  ],
  "module_breakdown": [
    {"module_id": "BC-03", "depends_on": [], "suggested_task_granularity": ["schema/migration", "aggregate + domain logic", "application service", "API endpoint(s)"], "mvp_alignment": 1},
    {"module_id": "BC-01", "depends_on": ["BC-03"], "suggested_task_granularity": ["schema/migration", "aggregate + domain logic", "application service", "API endpoint(s)", "event publisher"], "mvp_alignment": 1},
    {"module_id": "BC-02", "depends_on": ["BC-01"], "suggested_task_granularity": ["schema/migration", "aggregate + domain logic", "event consumer", "API endpoint(s) for reporting"], "mvp_alignment": 1}
  ],
  "diagram_specifications": [
    {
      "name": "context-map",
      "type": "context-map",
      "shows": "The three bounded contexts and their relationships from section 6."
    },
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
    {"requirement_id": "FR-005", "sections": ["7", "9", "10"]},
    {"requirement_id": "NFR-002", "sections": ["7", "9"]}
  ]
}
```

Notice the bounded contexts (BC-01/02/03) are the load-bearing structure
here: they show up in the strategic design sections, the tactical design,
the component architecture, the ADR, and finally the Module & Task
Breakdown Map. That's deliberate — a bounded context identified in section
5 should be traceable all the way through to a row in section 35, not
introduced once and forgotten.
