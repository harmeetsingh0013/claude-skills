# Mini-PRD: [Product / System Name]

Status: Draft / Review / Approved
Version: [X.Y]
Owner: [Name / Team]
Target Release: [Date / MVP]

---

## 1. Product Context

### 1.1 Problem Statement

What problem are we solving? Describe: the user/business problem; who
experiences it; why it matters; how it's currently handled, if relevant.

Problem:
[2-5 concise paragraphs]

### 1.2 Target Users / Actors

| User / Actor | Description | Primary Goal |
|---------------|--------------|----------------|

---

## 2. Product Goal

Primary Goal:
[One concise statement]

Secondary Goals:
- [Goal]

---

## 3. Success Criteria

| Goal | Success Metric | Target |
|------|-----------------|--------|

Keep product success metrics separate from engineering capacity/NFRs —
"100M requests/month" is a workload assumption (section 9), not a
product success metric.

---

## 4. MVP Scope

### 4.1 In Scope
What must exist for the MVP:
- [Feature / capability]

### 4.2 Out of Scope
What we are explicitly NOT building:
- [Feature]

This section exists specifically to prevent scope creep.

---

## 5. Core User Journeys

Describe the most important end-to-end product flows. No implementation
details.

### Journey 1 — [Name]
User -> Action -> System behavior -> Result

### Journey 2 — [Name]
...

---

## 6. Product Requirements

Only high-level product capabilities — detailed system behavior belongs
in the Functional Requirements document, not here.

### PR-001 — [Capability]
Description:
Priority: Must Have / Should Have / Could Have
Acceptance intent:
- [Expected outcome]

### PR-002 — [Capability]
...

---

## 7. Business Rules

Rules from the product/business domain. Avoid implementation details
(database indexes, caching technology, queues, specific frameworks).

- [Rule]

---

## 8. Product Analytics / Measurement

MVP Metrics:
- [Metric]

Deferred Analytics:
- [Metric]

Specify privacy-sensitive data explicitly where relevant.

---

## 9. Assumptions

User Assumptions:
- [Assumption]

Business Assumptions:
- [Assumption]

Workload Assumptions:
- [Expected users]
- [Expected requests]
- [Expected data volume]
- [Expected read/write ratio]

Technical Assumptions:
- [Assumption]

Workload assumptions can later be converted into measurable NFRs.

---

## 10. Constraints

Only constraints that genuinely affect the solution.

Business Constraints:
- [Constraint]

Regulatory / Compliance Constraints:
- [Constraint]

Technical Constraints:
- [Constraint]

Time / Cost Constraints:
- [Constraint]

---

## 11. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|

---

## 12. Requirement Handoff

The Mini-PRD intentionally does not contain detailed technical
requirements.

### Functional Requirements
Derive detailed requirements from this Mini-PRD.
Expected areas:
- [Area]

### Non-Functional Requirements
Derive measurable NFRs from the product goals, workload assumptions, and
constraints.
Expected areas:
- Availability, Latency, Throughput, Scalability, Durability, Security,
  Observability, Data retention, [Other]

---

## 13. Design Boundary

The Mini-PRD must remain architecture-neutral. Do not prescribe specific
databases, queues, caches, orchestration platforms, sharding strategies,
ID-generation algorithms, or a microservices-vs-monolith choice — those
decisions belong to the engineering/design stages that follow.

---

## Completeness Assessment

Mini-PRD status:
READY_FOR_FR

<or, if not:>

Mini-PRD status:
BLOCKED

Blocking issues:
- Question #4 in Open Questions must be answered before FR can proceed
  because ...
