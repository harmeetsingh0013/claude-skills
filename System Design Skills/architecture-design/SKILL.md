---
name: architecture-design
description: Produces a versioned, complete system-design/architecture document (with a machine-readable data contract covering components, data architecture, APIs, ADRs, security, scalability, resilience, observability, trade-offs, and Mermaid diagram specifications) from a Functional Requirements Document and a Non-Functional Requirements Document, as stage 3 of a four-stage design pipeline (functional-requirements → non-functional-requirements → architecture-design → mermaid-js). Use this when the user wants system architecture, technical design, a design doc, ADRs, or technology/component decisions for a product that has (or should have) FR and NFR documents, or explicitly asks to run/update the "architecture design" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. This is the one skill in the pipeline that makes technology and implementation decisions — the other requirements skills deliberately don't.
---

# Architecture Design

You own turning validated requirements into a complete, decided system
design. This is the only pipeline stage where naming a database, a queue,
a cloud service, or an API shape is correct rather than scope creep — but
every decision here should trace back to something in the FR or NFR
document, not to habit or default preference. Read
`references/pipeline-conventions.md` once at the start of a session if you
haven't already.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID, otherwise ask the user whether it's new
or existing, then confirm via `resolve-project`). This skill is never the
first stage run for a brand-new project, so you should normally be
*confirming* an ID the user already has. Every `pipeline_tool.py` call
below assumes a confirmed `--project <id>`, placed **before** the
subcommand.

## Input gate

Before doing anything else, check *both* required inputs:

```
python scripts/pipeline_tool.py --project <id> check-ready functional-requirements
python scripts/pipeline_tool.py --project <id> check-ready non-functional-requirements
```

If either fails, stop and report exactly which is missing, in this form:

```
ERROR:
Architecture Design requires both:
1. Functional Requirements Document
2. Non-Functional Requirements Document
```

only naming the one(s) that actually failed. Don't attempt to fill the gap
by inventing requirements or by asking the user to restate them from
scratch — the correct fix is to run the missing upstream skill.

If both succeed, load each `.md` and `.data.json`, then validate both data
contracts:

```
python scripts/pipeline_tool.py --project <id> validate-data functional-requirements
python scripts/pipeline_tool.py --project <id> validate-data non-functional-requirements
```

Record both `PASS`/`FAIL` results in Section 2 (Input Documents) of your
document. A `FAIL` on either is a blocking condition — don't design against
a structurally broken contract even if its status claimed READY.

## Validate before designing: conflict detection

Once both inputs pass validation, read them fully before writing anything,
and actively look for contradictions between them — don't take both
documents at face value just because they each individually passed. The
classic case: an FR implies a user/traffic scale the NFR document doesn't
support (or contradicts), e.g. "supports 10 million users" in FR against
"100 concurrent users" in NFR. Other contradictions are just as real: an
NFR latency target that's incompatible with an FR's described workflow, or
an NFR durability/compliance requirement an FR's described data flow can't
satisfy as written. Cross-reference by ID (FR-N's requirements array
against NFR-N's `related_fr`) — the structured data makes this a lot more
reliable than eyeballing prose.

If you find a genuine contradiction:

- Do not silently pick one side and design around it.
- Do not average or split the difference.
- Record it in Section 3 (Requirements Validation → Conflicts).
- Set the Completeness Assessment to `CONFLICT`, the envelope's `status` to
  `CONFLICT`, and add one `errors` entry per contradiction with
  `code: "CONFLICT_DETECTED"` and a plain-language `message` describing
  both conflicting statements and where they came from (FR-N vs NFR-N).
- Still write a document — but make it a short report of the conflict(s)
  rather than a full design, and still call `finalize`. A clearly reported
  conflict is a legitimate, useful pipeline output; a design built on an
  unresolved contradiction is not.

If no conflicts, proceed to design.

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version architecture-design`.
If it returns a `previous_doc_path`/`previous_data_path`, read both as your
baseline. Change only what the new/changed FR or NFR content actually
affects — preserve ADRs and decisions that remain valid, and add a new ADR
(don't silently rewrite an old one — mark the old one `Superseded by
ADR-N`) if a decision needs to change. Note what changed and why in the
envelope's `summary`.

## The reasoning chain: never skip straight to a technology

Every consequential decision should visibly follow:
**FR + NFR → architectural driver → architecture decision → technology
evaluation → technology decision.** See
`references/architecture-reasoning.md` for a full worked example (click
tracking → async event publication → queue technology choice). Collapsing
this into "we use Kafka because click tracking" is architecture invention,
not architecture design — it also makes the decision impossible to
revisit intelligently when a requirement changes later.

## What belongs in this document

Fill in `templates/architecture-design.md` exactly — it has 34 numbered
sections plus a Completeness Assessment; don't drop or reorder them, even
if a section ends up brief. Use `references/adr-format.md` for each ADR
entry and `references/architecture-reasoning.md` for the driver chain. See
`examples/url-shortener-architecture.md` for a fully worked excerpt plus
its matching `data.json`.

Section 34 (Mermaid Diagram Specification) is where you tell `mermaid-js`
what to produce: name, type, and what each diagram must show. List only
the diagrams this specific design actually warrants — not one of every
type by default.

Alongside the `.md`, produce a `.data.json` following
`schema/architecture-design.schema.json` — ADRs, components, diagram
specifications, and traceability all need structured entries, not just
prose. This is the contract `mermaid-js` will read.

## No hallucination

If a requirement is too vague to make a specific technology decision (e.g.,
NFR says "must scale" with no number), don't pick a technology to sound
decisive — note the gap in "Open Questions" and either make an explicitly
labeled assumption (stated as such, so it's easy to revisit) or set the
Completeness Assessment to `BLOCKED` if the gap is significant enough that
any design would be a guess.

## Completeness Assessment

```
Architecture status:
READY_FOR_MERMAID
```

or

```
Architecture status:
BLOCKED

Blocking issues:
- ...
```

or, if Section 3 found contradictions:

```
Architecture status:
CONFLICT

Conflicts detected:
- CONFLICT_DETECTED: FR-N says ... while NFR-N says ...
```

Set the same value in `data.json`'s `status` field
(`READY_FOR_MERMAID`, `BLOCKED`, or `CONFLICT`).

## Finishing

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version architecture-design`
2. Write `design-docs/<id>/architecture-design/v<version>.md` and
   `design-docs/<id>/architecture-design/v<version>.data.json`.
3. Record `inputs_consumed` for both `functional-requirements` and
   `non-functional-requirements` (version + hash from the `check-ready`
   output above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data architecture-design --path design-docs/<id>/architecture-design/v<version>.data.json`
5. Write the envelope to `design-docs/<id>/architecture-design/v<version>.envelope.json`,
   mapping your Completeness Assessment status per
   `references/pipeline-conventions.md`'s table, with
   `"next_skill": "mermaid-diagrams"` (set this even on `CONFLICT` status,
   since re-running after the conflict is resolved still leads there).
6. Run `python scripts/pipeline_tool.py --project <id> finalize design-docs/<id>/architecture-design/v<version>.envelope.json`
7. Report to the user the version produced, a short summary, whether any
   conflicts were found, and whether `mermaid-js` can now run.
