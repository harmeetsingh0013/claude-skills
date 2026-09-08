# Quality attribute categories to consider

Use this as a prompt, not a form to fill in mechanically — include a
category only if the FR document actually implies it matters.

## Performance & scale
- Latency (p50/p95/p99, per operation)
- Throughput (requests/sec, concurrent users, concurrent operations)
- Data volume growth over time

## Availability & reliability
- Uptime target (e.g., 99.9%)
- Acceptable downtime/maintenance windows
- Recovery time objective (RTO) / recovery point objective (RPO)
- Graceful degradation expectations under partial failure

## Data
- Durability target
- Retention period, and what happens at expiry
- Backup frequency (as a requirement, not "use tool X")
- Consistency expectations (e.g., "a user must see their own write
  immediately" — described behaviorally, not as "strong consistency" or
  a specific database's guarantee)

## Security & privacy
- Authentication strength requirements
- Authorization granularity (e.g., "a team member must not see another
  team's data")
- Encryption expectations (in transit, at rest) as a requirement, not an
  implementation
- Data classification / PII handling constraints
- Audit requirements (what must be recorded, not how)

## Compliance & regulatory
- Applicable regulations (GDPR, HIPAA, SOC 2, etc.) if the domain implies
  them — don't assume these without a signal from the FR document or the
  user; ask instead of guessing.
- Data residency / geographic constraints

## Usability & accessibility
- Accessibility standard to meet (e.g., WCAG level), if relevant
- Supported locales/languages, if implied

## Observability (as a requirement, not a tool choice)
- What must be measurable or auditable at a business level (e.g., "every
  click must be attributable to a link and timestamp")

## Cost & operational constraints
- Any explicit budget or resource constraint the user mentioned — record
  it as a constraint here; don't translate it into a technology choice.
