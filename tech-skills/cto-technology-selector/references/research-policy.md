# Evidence and research policy

Read this before making any recommendation that rests on a factual claim about a technology's current state — which is most recommendations.

## Why this matters

Training data ages. A "current" fact about a release version, a maintenance status, a pricing model, or a cloud service's availability can be stale or simply wrong by the time you're asked. Recommending a technology based on a remembered fact that has since changed is worse than saying "let me check."

**Default: verify current facts before recommending**, even for technologies you're confident about — PostgreSQL, React, AWS, whatever. This isn't about distrust of your own knowledge of stable concepts (how B-trees work, what ACID means, the CAP theorem) — it's specifically about anything that *changes over time*: versions, maintenance/EOL status, licensing, service availability, ecosystem maturity, known breaking changes, security advisories.

## What to verify

- Latest stable release
- Maintenance status (actively maintained? maintenance mode? abandoned?)
- End-of-life status and timeline
- Security status / known advisories
- Supported platforms
- Licensing
- Cloud-service availability (managed offerings, regions, tiers)
- Ecosystem maturity (library/tooling support for what you need)
- Official roadmap, if it affects the decision
- Compatibility with other selected technologies
- Known breaking changes relevant to the use case

## Source preference order

1. Official technology documentation
2. Official project repositories
3. Official release notes
4. Official standards/specifications
5. Official security advisories
6. Maintainer documentation/blogs
7. Reputable engineering organizations
8. Peer-reviewed or high-quality technical publications
9. Experienced engineering practitioners (well-known, identifiable, credible)
10. Community discussions — used cautiously, as a signal of real-world experience, not a source of fact

Marketing material is never independent evidence. Popularity is never proof of technical suitability — it's one weak signal among many about ecosystem health, nothing more.

## How to search

Search for the specific claim, not a generic vibe-check. Contrast:

- Bad: "Is PostgreSQL good?"
- Good: "PostgreSQL current supported versions," "PostgreSQL logical replication limitations," "PostgreSQL transaction isolation levels serializable performance"

Specific queries return verifiable facts. Generic queries return opinion pieces and marketing. Cite sources when making an externally verifiable claim.

## When evidence is incomplete or contradictory

- If a fact can't be verified: say "I could not verify this" rather than presenting a best guess as fact.
- If sources disagree: explain the disagreement rather than silently picking a side.
- If evidence is thin: say so, and let that inform the confidence level on the recommendation (see the confidence guidance in SKILL.md) rather than overstating certainty.

## Never fabricate

Benchmarks, product capabilities, release dates, version numbers, compatibility claims, pricing, vendor commitments, support status, performance characteristics, adoption statistics, security claims, customer references, standards compliance. If it's not in your verified evidence, it doesn't go in the recommendation as fact.
