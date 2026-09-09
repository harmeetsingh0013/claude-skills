# Worked example: Mini-PRD — TeamLink URL Shortener

This is the stage-0 document that precedes the functional-requirements
example (`url-shortener.md`) — read together, they show how a PR
(product requirement) here becomes an FR (functional requirement) there.

## Excerpt of the .md document

```markdown
# Mini-PRD: URL Shortener Service (MVP)

Status: Draft
Version: 1.0
Owner: Product / Engineering
Target Release: MVP

---

## 1. Product Context

### 1.1 Problem Statement

Long URLs can be difficult to share, read, and communicate, particularly
in channels with limited space or where compact URLs are preferred, such
as SMS, social-media posts, marketing campaigns, and printed materials.

The product will provide a service that converts a long destination URL
into a compact URL that users can share and later resolve to the original
destination.

### 1.2 Target Users / Actors

| User / Actor | Description | Primary Goal |
|---------------|--------------|----------------|
| Marketer / Creator | Creates links for campaigns or content | Generate a compact shareable URL |
| Application | Programmatically creates short URLs | Obtain a short URL through an API |
| End User | Opens a shortened URL | Reach the original destination |

---

## 2. Product Goal

Primary Goal:
Provide a simple and reliable service for creating and resolving short URLs.

Secondary Goals:
- Support custom aliases.
- Support optional link expiration.
- Capture basic usage information for future analytics.

---

## 3. Success Criteria

| Goal | Success Metric | Target |
|------|-----------------|--------|
| Reliable link creation | Successful creation rate | Defined in FR/NFR |
| Fast user experience | Redirect latency | Defined in NFR |

---

## 4. MVP Scope

### 4.1 In Scope
- Create short link (auto-generated code or custom alias)
- Redirect to destination
- Optional link expiration
- Basic analytics (click count, timestamp)

### 4.2 Out of Scope
- Advanced analytics dashboards, geographic/browser/device analytics
- Billing, QR-code generation, custom domains
- Persistent user accounts, authentication (MVP is anonymous)

---

## 6. Product Requirements

### PR-001 — Create Short Link
Description: The product shall allow a client to create a short URL from
a valid destination URL.
Priority: Must Have
Acceptance intent:
- Valid destination URLs can be shortened.
- Invalid destination URLs are rejected.
- Each created link receives a unique short identifier.

### PR-003 — Custom Alias
Description: The product shall allow a client to request a custom alias.
Priority: Must Have
Acceptance intent:
- The alias must comply with the product's character rules.
- The alias must be unique.

### PR-004 — Redirect
Description: The product shall redirect users from a valid short URL to
its destination URL.
Priority: Must Have
Acceptance intent:
- Valid links resolve to the correct destination.
- Expired links do not redirect.

---

## 9. Assumptions

Workload Assumptions:
- Up to 100 million new links/month.
- Redirect traffic substantially greater than creation traffic.
- Traffic distribution is highly skewed (a small number of links receive
  a large share of requests).

---

## 13. Design Boundary

This Mini-PRD deliberately does not prescribe implementation technology
(no Redis, PostgreSQL, DynamoDB, Kafka, CDN, microservices, sharding, or
ID-generation algorithm). Those decisions belong to the engineering
design process.

## Completeness Assessment

Mini-PRD status:
READY_FOR_FR
```

(trimmed for length — sections 5, 7, 8, 10, 11 follow the same pattern as
the full template; see `templates/mini-prd.md`)

## The matching data.json (excerpt)

```json
{
  "document_id": "PRD-TEAMLINK-001",
  "product": "TeamLink URL Shortener",
  "version": "1.0",
  "created": "2026-01-10",
  "status": "READY_FOR_FR",
  "blocking_issues": [],
  "owner": "Product / Engineering",
  "target_release": "MVP",
  "problem_statement": "Long URLs are hard to share and communicate in space-constrained channels (SMS, social media, print). The product converts a long destination URL into a compact, shareable URL that resolves back to the original.",
  "actors": [
    {"actor": "Marketer / Creator", "description": "Creates links for campaigns or content", "primary_goal": "Generate a compact shareable URL"},
    {"actor": "Application", "description": "Programmatically creates short URLs", "primary_goal": "Obtain a short URL through an API"},
    {"actor": "End User", "description": "Opens a shortened URL", "primary_goal": "Reach the original destination"}
  ],
  "primary_goal": "Provide a simple and reliable service for creating and resolving short URLs.",
  "secondary_goals": ["Support custom aliases.", "Support optional link expiration.", "Capture basic usage information for future analytics."],
  "success_criteria": [
    {"goal": "Reliable link creation", "metric": "Successful creation rate", "target": "Defined in FR/NFR"},
    {"goal": "Fast user experience", "metric": "Redirect latency", "target": "Defined in NFR"}
  ],
  "in_scope": ["Create short link (auto-generated code or custom alias)", "Redirect to destination", "Optional link expiration", "Basic analytics (click count, timestamp)"],
  "out_of_scope": ["Advanced analytics dashboards", "Geographic/browser/device analytics", "Billing", "QR-code generation", "Custom domains", "Persistent user accounts", "Authentication (MVP is anonymous)"],
  "user_journeys": [
    {"name": "Create Short Link", "steps": ["Client submits destination URL", "Validate request", "Generate or validate short code", "Store link", "Return short URL"]},
    {"name": "Redirect", "steps": ["End user requests short URL", "Resolve short code", "Determine link state", "Record required analytics", "Redirect to destination"]}
  ],
  "product_requirements": [
    {"id": "PR-001", "capability": "Create Short Link", "description": "The product shall allow a client to create a short URL from a valid destination URL.", "priority": "Must Have", "acceptance_intent": ["Valid destination URLs can be shortened.", "Invalid destination URLs are rejected.", "Each created link receives a unique short identifier."]},
    {"id": "PR-003", "capability": "Custom Alias", "description": "The product shall allow a client to request a custom alias.", "priority": "Must Have", "acceptance_intent": ["The alias must comply with the product's character rules.", "The alias must be unique."]},
    {"id": "PR-004", "capability": "Redirect", "description": "The product shall redirect users from a valid short URL to its destination URL.", "priority": "Must Have", "acceptance_intent": ["Valid links resolve to the correct destination.", "Expired links do not redirect."]}
  ],
  "business_rules": ["Every active short code identifies at most one destination.", "Custom aliases must be unique.", "Expired links must not redirect.", "Anonymous clients are subject to abuse/rate-control policies."],
  "mvp_metrics": ["Link identifier", "Successful redirect count", "Redirect timestamp"],
  "deferred_analytics": ["IP-based analytics", "Geographic analytics", "Browser/device analytics"],
  "assumptions": {
    "user": ["Users value compact, shareable URLs."],
    "business": ["Anonymous link creation is acceptable for the MVP."],
    "workload": ["Up to 100 million new links/month.", "Redirect traffic substantially greater than creation traffic.", "Traffic distribution is highly skewed."],
    "technical": ["Links may remain active for years unless an expiration date is specified."]
  },
  "constraints": {
    "business": [],
    "regulatory": [],
    "technical": ["MVP short codes are limited to seven characters."],
    "time_cost": []
  },
  "open_questions": [
    {"number": 1, "question": "Which destination URL schemes are supported?", "owner": "Product", "status": "Open"},
    {"number": 2, "question": "What HTTP redirect status code should be used?", "owner": "Engineering", "status": "Open"}
  ],
  "design_boundary_note": "No specific database, cache, queue, CDN, sharding strategy, or ID-generation algorithm is prescribed; those are engineering decisions for functional-requirements' downstream stages."
}
```

Notice `workload` under `assumptions` — this is the field
non-functional-requirements reads directly when it needs a concrete
number for a capacity-related NFR (e.g. "up to 100 million new links/month"
becomes the basis for a throughput target), per the note in section 9 of
the template ("Workload assumptions can later be converted into
measurable NFRs").

Also notice PR-001, PR-003, and PR-004 map directly onto FR-001, FR-002/
FR-003, and FR-004 in the functional-requirements worked example — that's
the `source_pr` field on each FR entry doing its job, not a coincidence.
