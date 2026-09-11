# Engineering Principles

## Pragmatic engineering

Apply the spirit of *The Pragmatic Programmer*: avoid duplication, keep abstractions understandable, automate repeatable work, make dependencies explicit, design for change, eliminate unnecessary complexity, fix problems at their source, and prefer simple solutions when they adequately satisfy requirements. These are tools, not dogma — a principle only matters insofar as it serves the actual requirements and constraints of the system in front of you.

## Clean code

Meaningful names, small and cohesive units, clear responsibilities, explicit dependencies, low accidental complexity, limited coupling, appropriate abstraction, readable control flow, maintainable tests. Don't turn this into rule-following theater ("every method must have N lines," "every class must have one method") — engineering judgment takes precedence over simplistic rules.

## Design patterns

Use established patterns (Gang of Four and beyond — creational, structural, behavioral, architectural, concurrency, integration) when they solve an actual problem you have. Don't introduce a pattern merely because it exists or because it's the "correct" textbook answer — prefer the simplest design that satisfies the requirements. A pattern that adds indirection without solving a real problem is speculative generalization, which is exactly the kind of thing to avoid.

## Anti-patterns to actively avoid

God objects/services, massive methods, excessive inheritance, inappropriate abstraction, speculative generalization, circular dependencies, tight coupling, shared mutable state, hidden global state, uncontrolled asynchronous execution, unbounded concurrency, blocking operations inside async paths, distributed monoliths, accidental complexity, premature optimization, cargo-cult patterns, unnecessary microservices, over-engineered abstractions.

If an existing anti-pattern in the codebase has to remain for now (e.g. a larger refactor is out of scope), document why rather than silently reinforcing it or silently fixing it out of scope.

## Language and paradigm independence

Adapt engineering decisions to the selected stack rather than forcing one paradigm everywhere. Be equally competent applying object-oriented, procedural, functional, generic, concurrent, asynchronous, actor-based, message-passing, parallel, and distributed-systems concepts — and use the idioms and conventions of whatever language the project actually uses (C, C++, Java, C#/.NET, Rust, Go, JavaScript/TypeScript, Python, Erlang/Elixir, and others). A Go service and a Java service that solve the same problem should look idiomatic in their own language, not like a translation of each other.

## Implementation standards

Implement the smallest maintainable solution that satisfies the requirements. Prefer clarity, cohesion, explicit dependencies, predictable behavior, testability, observability, and maintainability over speculative abstractions, unnecessary frameworks, unnecessary indirection, premature optimization, duplicate implementations, or hidden behavior. Don't rewrite unrelated code just because you'd have written it differently — see scope discipline in `reporting-and-status.md`.

## API and contract discipline

Preserve established contracts unless the Sprint explicitly requires a breaking change. When implementing or changing an API, think through: request validation, response contracts, error semantics, backward compatibility, idempotency, authentication, authorization, rate limiting where applicable, timeout behavior, and observability. Document any breaking change explicitly — don't let it slip in as a side effect.

## Database and persistence discipline

For any persistence change, evaluate schema compatibility, migrations, indexes, constraints, transactions, consistency, concurrency, rollback, data integrity, query performance, and backward compatibility. Never casually change assumptions about production data. If migration behavior is uncertain — e.g. whether a column can safely be dropped, whether a backfill is needed — stop and clarify rather than guessing; this is exactly the kind of decision that's expensive to get wrong after the fact.
