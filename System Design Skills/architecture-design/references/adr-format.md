# ADR format

Concise, per-decision. Number sequentially (ADR-001, ADR-002, ...). Only
write one for a genuinely significant, expensive-to-reverse decision —
not for every implementation detail.

```markdown
### ADR-003 — Use Postgres for link and click-event storage

**Status:** Accepted
**Driven by:** NFR-4 (write consistency), NFR-9 (durability)

**Context:** Link creation must be immediately consistent (FR-3: reject
duplicate custom codes within a team), and click events must be durably
recorded (NFR-9: 99.999999999% durability).

**Decision:** Use Postgres as the primary store for links and click events.

**Alternatives:**
- DynamoDB — rejected: the duplicate-short-code check (FR-3) needs a
  unique constraint enforced at write time across the team's existing
  codes, which is awkward without a relational unique index.
- MongoDB — rejected: no strong need for a flexible schema here, and the
  team has more relational-consistency requirements than document-shape
  flexibility needs.

**Trade-offs:** Gains strong uniqueness/transactional guarantees at the
cost of a relational schema-migration process; click event volume will
need a partitioning strategy revisited if throughput grows past NFR-2's
current target.
```

Four parts, always: **Context** (what forces this decision), **Decision**
(what was chosen, stated plainly), **Alternatives** (what else was
considered and why it lost), **Trade-offs** (what's given up, not just
what's gained — never present a decision as having none). Keep each ADR
self-contained — a reader should understand it without cross-referencing
three other sections.

When revising an existing architecture document, add a new ADR that
supersedes an old one rather than editing the old one in place (mark the
old one's status `Superseded by ADR-N`), so the document keeps a decision
history.
