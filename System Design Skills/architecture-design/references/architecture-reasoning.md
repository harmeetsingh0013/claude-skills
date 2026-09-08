# The reasoning chain architecture-design must follow

Never jump straight from a requirement to a named technology. Show the
intermediate steps — they're what makes an ADR defensible instead of a
guess, and they're what a reader (or a future revision) uses to tell
whether the decision still holds after something upstream changes.

```
FR: Track every click. (FR-005)
NFR: Click tracking must not increase redirect p99 latency. (NFR-002)
        │
        ▼
Architectural Driver:
Analytics must be decoupled from redirect processing.
        │
        ▼
Architecture Decision:
Publish click events asynchronously rather than writing them inline
during the redirect request.
        │
        ▼
Technology Evaluation:
Kafka / SQS / Pub/Sub / RabbitMQ / a simple in-process async write —
weighed against the actual NFRs (throughput, durability, operational
complexity for a small-team product), not against which is most popular.
        │
        ▼
Technology Decision:
[chosen technology + rationale tied back to the specific NFR values]
```

Each arrow is a place a reader might reasonably disagree with you — which
is exactly why it needs to be visible rather than collapsed into "we use
Kafka because click tracking." Skipping straight from FR/NFR to a
technology name is the same scope-creep failure the FR and NFR skills are
built to avoid, just one stage later: a technology choice that isn't
visibly derived from a requirement is architecture invention, not
architecture design.

This is also what makes conflict detection meaningful: if you can't
articulate the architectural driver a requirement produces, that's often a
sign the requirement itself is ambiguous or contradicts another one —
surface that in Section 3 (Requirements Validation) rather than pushing
through to a decision anyway.
