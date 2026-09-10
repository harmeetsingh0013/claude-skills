# Technology evaluation model

This is the reasoning framework behind every recommendation this skill makes, from a one-line technology question to a full stack decision.

## Six dimensions of fit

Evaluate any credible candidate technology against the actual system, not in the abstract, across:

**Functional fit** — Can it actually do what's required?

**Non-functional fit** — latency, throughput, availability, scalability, durability, consistency, fault tolerance, recoverability, security, observability, maintainability. Only the dimensions that matter for *this* system need deep evaluation — don't force a throughput analysis on a system with no throughput requirement.

**Architectural fit** — coupling, cohesion, boundaries, communication model, data ownership, deployment model, failure modes, scalability model, integration model, evolutionary characteristics (how easily it accommodates future change).

**Operational fit** — deployment complexity, monitoring, debugging, upgrades, backups, disaster recovery, incident response, the operational expertise it demands from whoever runs it.

**Team fit** — existing expertise, hiring availability, learning curve, developer productivity, testing ecosystem, tooling maturity.

**Economic and strategic fit** — infrastructure cost, licensing, operational cost, engineering cost, migration cost, opportunity cost, vendor lock-in, ecosystem health, longevity, interoperability, portability, future evolution and migration options.

## Technology decision categories

Consider decisions across whichever of these areas are relevant to the system at hand:

- **Application**: programming language, runtime, framework, API technology, serialization, validation, dependency management.
- **Data**: relational database, document database, key-value store, graph database, time-series database, analytical warehouse, object storage, cache, search engine.
- **Integration**: REST, GraphQL, gRPC, messaging, event streaming, webhooks, file-based integration, other protocols.
- **Infrastructure**: cloud platform, compute, containers, orchestration, serverless, networking, load balancing, storage.
- **Operations**: CI/CD, infrastructure as code, observability (logging, metrics, tracing, alerting), secrets management.
- **Security**: identity, authentication, authorization, key management, encryption, secrets, security monitoring.
- **AI/ML** (only when relevant): model provider, model family, inference architecture, embedding model, vector storage, retrieval architecture, evaluation infrastructure, agent framework, model gateway, observability, guardrails.

## The simplicity principle

Prefer the simplest architecture that satisfies the requirements. Complexity is a cost that has to be paid for in operational burden, cognitive load, and failure surface — every significant architectural technology needs a reason to exist beyond "it's what serious systems use."

Treat these as things that must be *justified by requirements*, not defaults to reach for:
microservices, event-driven architecture, Kubernetes, service meshes, distributed databases, message brokers, CQRS, event sourcing, polyglot persistence, serverless, complex caching layers, AI agents.

A distributed system should never be introduced merely because it sounds architecturally sophisticated. If a monolith on a single well-chosen database satisfies the actual requirements, that's the correct recommendation, even if it's the less exciting one.

## Avoiding cargo cults

None of the following, alone, justifies a recommendation:
- it's fashionable
- Netflix/Google/Amazon/OpenAI/Anthropic (or any other famous company) uses it
- it's labeled "cloud native," "enterprise grade," or "AI native"
- it's popular on GitHub or shows up constantly in job ads
- it happens to be the technology you know best

Always be able to answer: why does *this specific system*, with *its* requirements and constraints, need this technology? If the honest answer is "it doesn't materially matter, several options would work," say that too — false precision is its own kind of cargo cult.

## What to optimize for

fitness for purpose · simplicity · reliability · maintainability · operability · security · economics · team effectiveness · evolvability.

Not: novelty, popularity, personal familiarity, vendor marketing, resume value, architectural fashion, complexity for its own sake, or technological maximalism.

## Comparing candidates

Use a decision matrix (weighted criteria × candidates) when it genuinely improves clarity — but don't manufacture numerical scores just to make a decision look more scientific than it is. If you do score numerically, explain the scoring model and its limits plainly. Qualitative reasoning ("A is operationally simpler and the team already knows it; B's extra consistency guarantees aren't needed here") is often clearer and is entirely acceptable on its own.

Every recommendation should be able to answer two questions:
1. Why is this technology appropriate for this system?
2. What would cause us to choose something else instead?

A recommendation without that second answer — the counterfactual — is incomplete; it means you haven't actually located the decision's sensitivity to evidence or requirements changing.
