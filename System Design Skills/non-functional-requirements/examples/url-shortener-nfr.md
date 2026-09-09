# Worked example: Non-Functional Requirements — TeamLink (continued)

Derived from functional-requirements v1.0 (see url-shortener.md).

## Excerpt of the .md document

```markdown
## Document Metadata

Document ID: NFRD-TEAMLINK-001
Product: TeamLink URL Shortener
Version: 1.0
Created: 2026-01-16
Status: READY_FOR_ARCHITECTURE

## MVP Scope

MVP number: 1
New NFRs in this MVP: 9
Total NFRs included so far: 9
Is this the final MVP? No

## Functional Requirements Input

Input document: functional-requirements
Version: 1.0

Input validation:
PASS

## Performance Requirements

#### NFR-001
Related FR: FR-004 (redirect)
Metric: Redirect (FR-004) p99 latency
Target: < 100ms
Priority: P0
Rationale: A shortened link is meant to feel instantaneous; a slow
redirect defeats the product's purpose.

#### NFR-002
Related FR: FR-005 (click event recording)
Metric: Click event recording must not add latency to the redirect path
Target: Recording is decoupled from the redirect response
Priority: P0
Rationale: FR-005 explicitly says a recording failure must not block the
redirect — that only holds if recording happens out of the critical path.

## Requirements Traceability

| NFR | Related FR | Metric | Target | Priority |
|-----|------------|--------|--------|----------|
| NFR-001 | FR-004 | Redirect p99 latency | < 100ms | P0 |
| NFR-002 | FR-005 | Click recording latency impact | Decoupled from redirect | P0 |

## Completeness Assessment

Non-functional requirements status:
READY_FOR_ARCHITECTURE
```

## The matching data.json (excerpt)

```json
{
  "document_id": "NFRD-TEAMLINK-001",
  "product": "TeamLink URL Shortener",
  "version": "1.0",
  "created": "2026-01-16",
  "input_document": {"type": "functional-requirements", "version": "1.0", "validation": "PASS"},
  "status": "READY_FOR_ARCHITECTURE",
  "blocking_issues": [],
  "mvp": {"number": 1, "new_in_this_mvp": 9, "total_included": 9, "is_final": false},
  "nfrs": [
    {
      "id": "NFR-001",
      "category": "Performance",
      "related_fr": ["FR-004"],
      "metric": "Redirect p99 latency",
      "target": "< 100ms",
      "priority": "P0",
      "mvp_number": 1
    },
    {
      "id": "NFR-002",
      "category": "Performance",
      "related_fr": ["FR-005"],
      "metric": "Click event recording latency impact on redirect",
      "target": "Decoupled from redirect path",
      "priority": "P0",
      "mvp_number": 1
    }
  ],
  "conflicts": [],
  "open_questions": [],
  "traceability": [
    {"nfr": "NFR-001", "related_fr": ["FR-004"], "metric": "Redirect p99 latency", "target": "< 100ms", "priority": "P0"},
    {"nfr": "NFR-002", "related_fr": ["FR-005"], "metric": "Click event recording latency impact", "target": "Decoupled from redirect path", "priority": "P0"}
  ]
}
```

NFR-002 is the important one to notice: it doesn't say "use a queue." It
says *what must be true* (recording can't add redirect latency). That
constraint is exactly what lets architecture-design derive "publish click
events asynchronously" as a decision, and then evaluate specific
technologies against it — see the architecture-design example.
