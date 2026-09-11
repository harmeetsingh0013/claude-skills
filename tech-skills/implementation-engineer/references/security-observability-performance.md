# Security, Observability, Performance

## Security

Treat security as part of implementation correctness, not a separate pass. Where applicable, consider: authentication, authorization, input validation, injection, secrets management, sensitive-data exposure, dependency vulnerabilities, insecure defaults, logging of sensitive data, SSRF, path traversal, deserialization, cryptographic misuse, and privilege boundaries. Follow explicit project security requirements and established secure defaults — don't invent security requirements that aren't grounded in the project or a real risk you've identified.

## Observability

For production systems, consider structured logging, metrics, tracing, health checks, meaningful error information, correlation/request IDs, and operational diagnostics. Add observability because it serves a diagnostic purpose, not as noise — and never log secrets or sensitive data just because it's convenient for debugging.

## Performance

Don't optimize without evidence. When performance genuinely matters: identify the actual performance requirement, identify the bottleneck, measure where practical, choose the least complex effective optimization, and verify the result. Speculative optimization — tuning something that isn't actually a bottleneck — is a cost, not a benefit.
