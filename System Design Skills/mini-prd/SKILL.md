---
name: mini-prd
description: Interviews the user in depth to produce a versioned Mini-PRD (product context, goals, success criteria, MVP scope, user journeys, high-level product requirements, business rules, assumptions, and constraints) from a raw problem/idea description, as stage 0 (the first stage) of a five-stage design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js). Use this whenever the user describes a problem or product idea and wants it turned into a proper product brief before requirements work starts, when starting a brand-new project through the design pipeline, or when explicitly asked to run/update the "mini-PRD" / "PRD" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. This is architecture-neutral and technology-neutral — it never prescribes a database, queue, cache, or specific technology; those decisions belong to architecture-design, several stages later.
---

# Mini-PRD

You own turning a raw problem description into a shared, agreed
understanding of *what* problem is being solved and *why* — not how it
will be built, and not the detailed system behavior (that's
functional-requirements' job, next). Read `references/pipeline-conventions.md`
once at the start of a session if you haven't already; it defines the
project-ID scheme, the two-file document contract (`.md` + `.data.json`),
and the versioning script every pipeline skill shares.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure. Since this
is normally the *first* stage invoked for a brand-new product, you're
often the one asking "new project, existing ID, or a path to existing
documents? If it's new, what should I call it, and where would you like
the documents saved? (I can use the default location if you don't have a
preference.)" and minting the ID via
`resolve-project --name "<short name>" --location "<path>"` (omit
`--location` only if the user explicitly said to use the default). Every
`pipeline_tool.py` call below assumes you've done this and shows
`--project <id>` accordingly — always place it **before** the subcommand.

## Input

The only required input is a raw problem/idea description. There's no
upstream document to gate on — this is the one skill in the pipeline with
no `check-ready` gate (functional-requirements gates on *your* output,
not the other way around).

- If the user gave you a description directly, record it:
  `echo "<description>" | python scripts/pipeline_tool.py --project <id> set-idea`
- If one's already recorded for this project and the user hasn't given
  you new text, use the existing one — read it with
  `python scripts/pipeline_tool.py --project <id> latest product-idea`.
- If neither exists, ask for it. A one-line idea is a fine *starting*
  point — the interview below is what turns it into something usable; you
  don't need a fully-formed description upfront.

## Interview relentlessly — this is the core of the skill

A one-paragraph idea is never enough to fill out a real PRD, and guessing
the gaps defeats the purpose of this stage. Interview the user until you
and they share a concrete, unambiguous understanding of the problem and
the solution, section by section, following `templates/mini-prd.md`'s
order (problem statement → actors → goals → success criteria → MVP scope
→ user journeys → product requirements → business rules → analytics →
assumptions → constraints → open questions).

**Ask one focused question at a time, not a checklist dump.** A wall of
fifteen questions gets skimmed and half-answered; one clear question gets
a real answer. Batch at most two or three tightly related questions when
they're genuinely inseparable (e.g. "who are the primary users, and what
does each one want out of this?").

**Walk down each branch to resolution before moving to the next one.**
When an answer opens a new, dependent question, follow it immediately
rather than filing it away for later — resolving a whole branch of
related decisions together keeps the user in the context where they can
actually reason about it. For example: user says custom aliases should be
supported → immediately ask what characters are allowed → then whether
aliases are globally or per-team unique → then what happens on collision
→ *then* move to the next branch (e.g. link expiration). Don't jump
between unrelated topics and back — it fragments the user's attention and
tends to produce inconsistent answers.

**Cover every section — don't skip ones that seem obvious.** If something
seems implied, confirm it explicitly rather than silently assuming it
("So anonymous usage is fine for the MVP, no accounts needed — is that
right?") — a wrong silent assumption is more expensive to discover later
than one extra confirming question now.

**Stay architecture-neutral, actively.** If the user starts describing
technology ("we'll use Postgres and Redis"), don't let it drive the
product conversation — redirect toward the underlying need ("what about
this makes you want fast lookups / durability?"), and if it's a genuine
constraint (e.g. "must run in our existing AWS account," a real
regulatory requirement), record it under Constraints rather than letting
it silently become a product decision. See section 13 (Design Boundary)
and don't yourself suggest a database, queue, cache, or specific
technology at any point in this interview — that's several stages away.

**Knowing when to stop:** you're done with a section when you could fill
its part of the template without guessing. You're done with the whole
interview when every section is either filled or the user has explicitly
said to leave something as an open question and move on — don't interview
forever chasing a perfect document; log genuine unresolved items in
section 11 (Open Questions) instead of blocking indefinitely on them. Use
the Completeness Assessment (below) to distinguish "some open questions
remain, but nothing blocks FR" from "this can't proceed yet."

## No hallucination

Every filled-in section should trace to something the user actually
said, not to what would make a tidy-looking document. If the user hasn't
told you something and you can't reasonably infer it from what they have
said, that's an open question, not a gap to quietly fill in. This applies
especially to Success Criteria, Workload Assumptions, and Constraints —
invented numbers here become invented capacity requirements two stages
later in non-functional-requirements, which is a more expensive place to
discover they were never real.

## MVP Scope here vs. MVP batching downstream — don't conflate them

Section 4 (MVP Scope: In Scope / Out of Scope) is a single, upfront
product-level scoping decision — it does not use the `mvp.number`
batch-progression object that functional-requirements, non-functional-
requirements, and architecture-design carry (see
`references/pipeline-conventions.md`'s "Working in MVP-sized batches").
This document doesn't need one; it's produced once (and revised via
ordinary version bumps if the product scope genuinely changes), not
produced in ~10-item batches the way FR's requirements list is.

What this section *does* do: your In Scope list is what
functional-requirements uses to prioritize its first batch, and your Out
of Scope list becomes the seed for its backlog — so a clear, well-reasoned
split here saves real duplicated effort downstream. See
`examples/url-shortener-prd.md`.

## Document structure

Fill in `templates/mini-prd.md` exactly — don't drop or reorder its 13
sections, even if one ends up brief (write "None identified" rather than
omitting a section). Each product requirement gets its own `#### PR-NNN`
block. See `examples/url-shortener-prd.md` for a fully worked document
plus its matching `data.json` — notice how its `PR-NNN` entries become
`FR-NNN` entries (via the `source_pr` field) in the functional-
requirements worked example.

Alongside the `.md`, produce a `.data.json` following
`schema/mini-prd.schema.json` — actors, success criteria, in/out of
scope, user journeys, product requirements, business rules, assumptions,
constraints, and open questions all need structured entries, not just
prose. This is the contract `functional-requirements` will read; its
`assumptions.workload` array specifically is what `non-functional-
requirements` reads later for capacity-related targets.

## Completeness Assessment

```
Mini-PRD status:
READY_FOR_FR
```

or

```
Mini-PRD status:
BLOCKED

Blocking issues:
- Open question #4 must be answered before FR can proceed because ...
```

Set the same value in `data.json`'s `status` field (`READY_FOR_FR` or
`BLOCKED`), and list the same issues in `blocking_issues`. Reserve
`BLOCKED` for genuine must-resolve gaps (e.g. the core problem itself is
still unclear) — a handful of open questions that don't block FR from
starting (like "what HTTP status code for redirects?") belong in section
11, not as a blocker.

## Human review checkpoint — before writing anything to disk

The interview itself is the primary review mechanism, but don't finalize
straight out of the last interview answer. Once you believe you have
everything, draft the complete document **directly in your response**,
not to disk yet, and walk through it section by section (or a clear
summary if it's long) — this is the first time the user sees it assembled
as a whole, and assembly often surfaces a gap or inconsistency that didn't
show up answering one question at a time. Then explicitly ask something
like: *"Here's the complete Mini-PRD. Does this accurately capture the
problem and what we're building for the MVP — anything to correct or
add before I lock this in as v\<version\> and hand off to functional
requirements?"* Stop and wait for their reply in a new turn.

If they want changes, revise and ask again. Repeat until the user
explicitly confirms, or explicitly tells you to proceed without further
review. This applies even when the orchestrator invoked you.

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version mini-prd`.
   If it returns a `previous_doc_path`/`previous_data_path`, this is a
   revision — read both as your baseline and change only what's actually
   different, the same incremental-update discipline every other stage
   follows.
2. Write `<project-root>/mini-prd/v<version>.md` (from the template) and
   `<project-root>/mini-prd/v<version>.data.json` (per the schema) —
   `<project-root>` is the `path` from Step 1's `resolve-project` output.
3. Hash the product idea input: `python scripts/pipeline_tool.py --project <id> latest product-idea`
   (use its `hash` and `version` in your envelope's `inputs_consumed`).
4. Validate your own data file before finalizing:
   `python scripts/pipeline_tool.py --project <id> validate-data mini-prd --path <project-root>/mini-prd/v<version>.data.json`
   — fix any reported errors before proceeding.
5. Write the envelope to `<project-root>/mini-prd/v<version>.envelope.json`
   per `references/pipeline-conventions.md`'s schema, mapping your
   Completeness Assessment status to the envelope `status` per that doc's
   mapping table, with `"next_skill": "functional-requirements"`.
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/mini-prd/v<version>.envelope.json`
7. Report to the user: the project ID (if newly minted, remind them to
   save it), the version produced, a short summary, and — if status is
   READY — that `functional-requirements` can now run. If you weren't
   invoked directly by the user, still report this back rather than
   silently continuing — the orchestrator checks in with the user between
   stages.

Your final output to the user/orchestrator is the document, the data
file, and the envelope. Don't narrate the interview transcript as part of
the deliverable — the finished document, not the process, is what gets
written.
