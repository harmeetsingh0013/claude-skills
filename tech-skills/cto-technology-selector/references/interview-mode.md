# Adaptive interview mode

Read this when no usable design documents exist and you need to collect enough information from the user directly to make a defensible technology decision.

## Principle

Ask only questions that can materially change the technology decision. Every question should be earning its place — if you already know the answer wouldn't move the recommendation, don't ask it.

## Calibrating depth to stakes

Before diving into the full question bank, get a rough sense of what's at stake — sometimes this takes one clarifying question, sometimes it's obvious from how the user described the system:

- **Low stakes** (prototype, internal tool, personal project, proof of concept, "just exploring"): ask the 2-4 questions that would most change the shape of the recommendation (typically: what problem, rough scale, and any hard constraints like "must run on our existing AWS account" or "team only knows Python"). Then make reasonable assumptions for the rest and state them plainly alongside the recommendation.
- **High stakes** (production system, customer-facing, handles money/health/personal data, expected to scale significantly, long expected lifetime, regulated industry): work through more of the question bank below before recommending — the cost of a wrong assumption is much higher, and the user is more likely to want to see your reasoning before you commit to a stack.
- **Uncertain**: ask directly. "Is this heading to production, or is it a prototype/internal tool?" is itself a high-value question that resolves how hard to press on everything else.

## The question bank, roughly in priority order

- What problem are we solving?
- Who are the users or consuming systems?
- What are the primary workflows?
- What are the expected request/transaction volumes?
- What latency is required?
- What availability is required?
- What consistency guarantees are required?
- What data is stored, and what are its relationships and access patterns?
- Is the workload synchronous, asynchronous, streaming, batch, or mixed?
- What integrations are required?
- What security or compliance requirements exist?
- Where will the system run — cloud, on-premises, hybrid?
- What existing technologies must be retained?
- What skills does the engineering team already have?
- What is the expected lifetime of the system, and rate of change?
- What is the budget or cost sensitivity?
- Is avoiding vendor lock-in important?
- Is time-to-market more important than long-term optimization?
- Are there hardware constraints?

Not every question applies to every system. A single-developer prototype doesn't need a consistency-guarantee conversation; a payments system does.

## The loop

After each answer:
1. Update your internal model of the system.
2. Note which technology decisions just became more (or fully) constrained.
3. Drop any remaining question that's no longer relevant given the new information.
4. Ask the next highest-value remaining question — never one already answered.

Stop as soon as you have enough for a defensible recommendation. You're allowed — expected, even — to make reasonable assumptions for anything unlikely to change the outcome. Whatever you assume, name it explicitly when you deliver the recommendation, so the user can correct it if you guessed wrong.
