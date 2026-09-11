# Concurrency and Asynchronous Programming

Treat concurrency as a correctness concern, not a performance feature. Don't introduce concurrency unless there's a demonstrated requirement or benefit — unbounded or uncontrolled concurrency is an anti-pattern, not a default.

Before implementing anything concurrent or asynchronous, reason through:

- ownership
- shared state
- synchronization
- ordering
- visibility
- atomicity
- cancellation
- failure propagation
- backpressure
- resource exhaustion
- deadlocks, livelocks, starvation
- race conditions
- scheduling
- bounded vs. unbounded concurrency
- task lifetime
- timeout behavior
- retries
- idempotency

Prefer structured, understandable concurrency over clever-but-opaque approaches.

When concurrency genuinely is required, be able to explicitly answer:

1. What executes concurrently?
2. Why is concurrency required here (what would be lost by making it sequential)?
3. What state is shared across the concurrent paths?
4. How is synchronization achieved?
5. How does cancellation work?
6. How do failures propagate out of the concurrent work?
7. How are resources (threads, connections, memory) bounded?
8. How is correctness tested — race conditions, cancellation, ordering, timeouts, failure paths?

If you can't answer these, that's a signal the design isn't ready to implement yet, not a detail to fill in with a guess while coding.
