# Final technology-stack document

Use this exact structure when the user wants a complete, final technology recommendation delivered as a document — not for quick questions or exploratory discussion (see "Output behavior" in SKILL.md for when this applies).

Write it as a Markdown file to `/mnt/user-data/outputs/<descriptive-name>.md` and present it with `present_files`. Keep the in-chat message brief — the document is the deliverable, not a chat wall of text.

## Structure

```markdown
# Technology Stack Recommendation: [System Name]

## 1. Executive Summary
The recommended stack in a few sentences, and the major architectural reasoning behind it.

## 2. System Context
What the system does, who it serves, and the scale/environment it operates in.

## 3. Requirements Influencing Technology
The functional and non-functional requirements that materially affected technology selection. Only the ones that actually drove a decision — don't pad this with irrelevant requirements.

## 4. Architectural Drivers
The constraints and architectural characteristics (consistency needs, failure-mode tolerance, latency budget, team shape, etc.) that shaped the decisions.

## 5. Recommended Technology Stack
For each technology selected:
- **Technology** (and version, where the version materially matters)
- **Architectural role**
- **Purpose**
- **Rationale**
- **Important alternatives considered**
- **Operational implications**
- **Risks**
- **Confidence**: High / Medium / Low
- **Evidence**: what was verified, and how (cite sources for externally verifiable claims)

## 6. Technology Decision Matrix
A concise comparison of the major decisions — qualitative or lightly weighted, per the guidance in evaluation-model.md. Don't force numeric scores where they don't add clarity.

## 7. Architecture Mapping
Map each selected technology to the architectural component or responsibility it supports, so a reader can see the system's shape from the stack alone.

## 8. Alternatives
Credible alternatives that were seriously considered, and why they weren't selected — not a token list, an honest account of the runner-up options.

## 9. Risks and Mitigations
Technology-specific risks and how they'd be controlled or monitored.

## 10. Evolution Strategy
How the stack can evolve as requirements change — what's cheap to change later, what's expensive, where the seams are.

## 11. Migration Considerations
When an existing system is involved: what migration actually looks like, its cost, and its risk. Omit this section entirely for greenfield systems.

## 12. Assumptions
Every assumption that materially influenced the recommendation, stated explicitly — especially any made during an abbreviated interview. The user should be able to read this section alone and know exactly what to correct if an assumption was wrong.

## 13. Open Decisions
Decisions intentionally left open — because evidence was insufficient, because they don't need to be made yet, or because they're genuinely close calls the user should weigh in on.

---

## Appendix: Technology Selection Rationale

For **every major technology decision**, in this exact format:

**Decision:** [what was being decided]
**Selected technology:** [the choice]

**Problem:** What problem must this technology solve?

**Requirements:** Which requirements influenced the decision?

**Alternatives:** What credible alternatives were evaluated?

**Evidence:** What evidence supports the evaluation? (cite sources)

**Trade-offs:** Advantages and disadvantages of the selection.

**Why selected:** Why this is the best fit for *this* system specifically.

**Why not alternatives:** Why the alternatives were rejected.

**Risks:** What could go wrong.

**Mitigation:** How those risks are controlled.

**Reversibility:** How difficult it would be to change this decision later.

**Confidence:** High / Medium / Low
```

## Notes on filling this in

- Don't manufacture content for a section that genuinely doesn't apply (e.g. section 11 for a greenfield build) — say it's not applicable and move on, rather than padding.
- Every claim that's externally verifiable (a version number, a licensing term, a release date) should trace back to something actually checked per `research-policy.md` — not recalled from memory.
- The appendix is the "show your work" section — it should let a skeptical senior engineer reconstruct your reasoning and disagree with a specific step, not just the conclusion.
