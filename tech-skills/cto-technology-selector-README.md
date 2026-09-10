# cto-technology-selector

A Claude skill that acts as a pragmatic CTO / software architect to select an appropriate technology stack for a software system — grounded in that system's actual requirements, not fashion, familiarity, or what famous companies use.

## What it does

When triggered, the skill:

1. **Looks for design documents first** — mini-PRDs, functional/non-functional requirements, architecture designs, ADRs, Mermaid diagrams, deployment docs, API specs, etc. If you point it at real documents, it inspects and cross-checks them before recommending anything, rather than trusting filenames or skipping straight to a guess.
2. **Runs an adaptive interview if there's nothing to inspect** — a handful of high-value questions for a low-stakes prototype, more for a production/regulated system. It never re-asks something you already answered, and it flags every assumption it makes instead of silently filling gaps.
3. **Verifies current facts before recommending** — always checks things like latest stable release, maintenance/EOL status, licensing, and known limitations rather than relying on (potentially stale) training data, even for well-known technologies.
4. **Evaluates candidates on six dimensions** — functional, non-functional, architectural, operational, team, and economic/strategic fit — and refuses to recommend something just because it's trendy, "AI-native," or what Netflix/Google/Amazon happen to use.
5. **Defaults to the simplest architecture that satisfies the requirements.** Microservices, Kubernetes, event sourcing, CQRS, distributed databases, message brokers, and similar have to be justified by an actual requirement, not assumed.
6. **Matches its response to the size of the question.** A quick "Kafka or RabbitMQ?" gets a direct answer with a counterfactual — not a 13-section report. A request for a full recommendation gets the full document.
7. **Handles pushback properly.** If you challenge a recommendation, it investigates the concern honestly and will reverse its own recommendation when the evidence supports it — rather than defending its first answer.
8. **Delivers final recommendations as a real file.** When you ask for a complete stack decision, it writes a structured Markdown document (executive summary → recommended stack → decision matrix → risks → evolution strategy → a fully-reasoned appendix per decision) to a downloadable file, not just a chat wall of text.

## Philosophy

The reasoning lens is Fowler-inspired (evolutionary architecture, YAGNI, architecture as "the decisions that are hard to change later") combined with a Kleppmann-style treatment of data-intensive and distributed systems (consistency models, replication, partitioning, failure modes, local-first trade-offs). These inform *how it reasons*, not name-dropping — the skill cites the underlying engineering principle, never the author, when explaining a decision.

## Domain boundary

In scope: software engineering, software architecture, distributed systems, application architecture, cloud/infrastructure, databases, languages, frameworks, APIs/protocols, messaging, observability, security engineering, DevOps/CI-CD, data platforms, AI/ML infrastructure, developer tooling, and hardware — but only where hardware materially affects a software decision (e.g. GPU requirements for an inference workload).

Out of scope: writing application code, general programming help unrelated to technology selection, and non-software domains (legal, financial, business strategy, mechanical/electrical engineering beyond software impact). The skill will say so and redirect if a request drifts there.

## How to trigger it

It's built to trigger on things like:
- "What tech stack should we use for [system]?"
- "Help me choose a database/framework/language for X"
- "Review our architecture docs and recommend technologies"
- "Should we use gRPC or REST here?" / "Is Kafka overkill for this?"
- Sharing a mini-PRD, requirements doc, architecture-design doc, ADR, or Mermaid diagram and asking for technology decisions from it

It's intentionally tuned to also catch narrow, single-technology questions — not just full "design my stack" requests — since the same evidence-based evaluation applies at any scale.

## File structure

```
cto-technology-selector/
├── SKILL.md                          — core workflow, persona, and pointers (~95 lines)
└── references/
    ├── document-discovery.md         — how to inspect supplied design docs, incl. staged pipelines
    ├── interview-mode.md             — the adaptive interview question bank + depth calibration
    ├── evaluation-model.md           — six-dimension fit model, decision categories, simplicity principle
    ├── research-policy.md            — evidence/source-ordering policy, current-state verification
    ├── disagreement-protocol.md      — how to handle pushback and existing-technology replacement asks
    └── output-document.md            — exact structure of the final technology-stack document
```

`SKILL.md` stays short and loads first; the reference files only get pulled in when the relevant step of the workflow is actually reached, so the skill doesn't burn context on, say, the full interview question bank when you've already handed it complete architecture documents.

## Configuration choices baked in

These were decided with you when the skill was built, and are worth knowing if you ever want to adjust them:

| Decision | Choice made |
|---|---|
| Final document delivery | Real downloadable `.md` file, not just inline chat text |
| Interview depth | Adaptive — scales to how high-stakes the system sounds, rather than always lean or always thorough |
| Research policy | Always verify current facts (versions, EOL, licensing, etc.) before recommending, even for well-known stable technologies |

If you want to change any of these later, the relevant instruction lives in `SKILL.md` (delivery format, under "Output behavior") or `references/interview-mode.md` (depth calibration) / `references/research-policy.md` (verification default).

## Test cases

`evals/evals.json` (packaged separately from the `.skill` file) has 4 realistic test prompts covering: a low-stakes scoped recommendation, a high-stakes document-driven analysis (including the case where referenced files aren't actually attached), a quick single-technology question, and a pushback/disagreement scenario. Useful as a regression check if you modify the skill later.

## Updating this skill

If you want to revise it — tighten a section, add a new reference file, change the output template — edit the relevant file directly and re-package with skill-creator's `package_skill.py`, or just ask Claude to do it for you with the skill-creator skill.
