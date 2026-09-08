# ADR format

One entry per consequential decision. Number sequentially (ADR-1, ADR-2, ...).

```markdown
### ADR-3: Use Postgres for link and click-event storage

**Status:** Accepted
**Driven by:** NFR-4 (write consistency), NFR-9 (durability)

**Context:** Link creation must be immediately consistent (FR-3: reject
duplicate custom codes within a team), and click events must be durably
recorded (NFR-9: 99.999999999% durability).

**Decision:** Use Postgres as the primary store for links and click events.

**Alternatives considered:**
- DynamoDB — rejected: the duplicate-short-code check (FR-3) needs a
  unique constraint enforced at write time across the team's existing
  codes, which is awkward without a relational unique index.
- MongoDB — rejected: no strong need for a flexible schema here, and the
  team has more relational-consistency requirements than document-shape
  flexibility needs.

**Consequences:** Introduces a relational schema migration process; click
event volume will need partitioning strategy revisited if throughput grows
past NFR-2's current target.
```

Keep each ADR self-contained — a reader should understand the decision
without cross-referencing three other sections. When revising an existing
architecture document, add a new ADR that supersedes an old one rather than
editing the old one in place (mark the old one's status as `Superseded by
ADR-N`), so the document keeps a decision history.
