---
name: functional-requirements
description: Produces a versioned Functional Requirements Document (with a machine-readable data contract) from a product idea, as stage 1 of a four-stage design pipeline (functional-requirements → non-functional-requirements → architecture-design → mermaid-js). Use this whenever the user describes a product idea, feature, or app concept and wants requirements captured, or explicitly asks to run/update the "functional requirements" stage of the design pipeline. Also use it when re-invoked by the design-pipeline-orchestrator skill. Do not use this for non-functional/quality requirements (throughput, latency, availability) or for anything architectural (databases, APIs-as-implementation, cloud services) — those belong to the other pipeline skills.
---

# Functional Requirements

You own **what the product must do** — nothing about how well it does it,
and nothing about how it's built. Read `references/pipeline-conventions.md`
once at the start of a session if you haven't already; it defines the
project-ID scheme, the directory layout, the two-file document contract
(`.md` + `.data.json`), and the versioning script every pipeline skill
shares.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID, otherwise ask the user whether it's new
or existing, then mint or confirm via `resolve-project`). Every
`pipeline_tool.py` call below assumes you've done this and shows
`--project <id>` accordingly — always place it **before** the subcommand.

A project ID being already present when the user starts talking to you is
itself informative: it means you're likely resuming, not starting fresh —
run `plan` (see Finishing) or just proceed with the idea they give you,
which `next-version` will treat as a revision automatically.

## Input

The only input is the product idea. There is no upstream document to
validate — this is the one skill in the pipeline with no `check-ready` gate.

- If the user gave you the idea directly in conversation, record it:
  `echo "<idea text>" | python scripts/pipeline_tool.py --project <id> set-idea`
- If `design-docs/<id>/product-idea/LATEST.json` already exists and the
  user hasn't given you new idea text, use the existing one — read it with
  `python scripts/pipeline_tool.py --project <id> latest product-idea` and
  load the file at `doc_path`.
- If neither exists, ask the user for the product idea. Don't invent one.

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version functional-requirements`.
If it returns a `previous_doc_path`/`previous_data_path`, read both — you're
revising the document, not starting fresh. Keep everything that's still
true (including FR-N numbering — never renumber an existing requirement
just because you're producing a new version); change only what the new or
updated idea actually implies changed. Say what changed in your envelope's
`summary`.

## Scope discipline

This is the easiest place for scope creep to sneak in, because it's
tempting to sound more concrete by naming a technology. Resist it. A
requirement describes an observable capability or constraint on behavior;
it does not name a database, a message broker, a cloud provider, a
programming language, an API shape, or a deployment topology. If you catch
yourself writing a verb like "expose," "deploy," "provision," or "index,"
stop and ask whether you're describing behavior (keep it) or a solution
(cut it — leave it for architecture-design to decide).

- Good: "The system must allow authenticated users to create shortened URLs."
- Not this: "The system will expose `POST /v1/urls` through an API Gateway."
- Good: "The system must notify a user when their upload finishes processing."
- Not this: "The system will publish an event to a Kafka topic on upload completion."

You *can and should* capture functional behavior that happens to involve
APIs, authentication, events, or integrations — just describe the observable
requirement, not the implementation.

## Document structure

Fill in `templates/functional-requirements.md` exactly — don't drop or
reorder its sections, even if a section ends up brief (write "None
implied by the idea" rather than omitting a section). Each individual
requirement gets its own `#### FR-NNN` block with every field the template
lists (Name, Actor, Priority, Description, Preconditions, Trigger, Main
Flow, Alternative Flows, Failure Behavior, Business Rules, Dependencies) —
group requirements under `### <Capability>` headings. See
`examples/url-shortener.md` for a fully worked document plus its matching
`data.json`.

Alongside the `.md`, produce a `.data.json` following
`schema/functional-requirements.schema.json` — every requirement, the
traceability table, and the completeness status need a structured
equivalent, not just prose. This is the actual contract
`non-functional-requirements` will read.

## No hallucination

If the product idea is too vague to derive real requirements (e.g., "build
me an app"), don't invent a fictional feature set to fill the template.
Write your best-effort interpretation plus the specific questions that
would unblock you into "Open Questions," and set the Completeness
Assessment to `BLOCKED` with those questions listed as blocking issues. A
short, honest document beats a long, made-up one.

## Completeness Assessment

The last section of the document is a machine-readable gate for the next
skill:

```
Functional requirements status:
READY_FOR_NFR
```

or

```
Functional requirements status:
BLOCKED

Blocking issues:
- FR-023 requires clarification because ...
- FR-041 conflicts with FR-018 because ...
```

Set the same value in `data.json`'s `status` field
(`READY_FOR_NFR` or `BLOCKED`), and list the same issues in
`blocking_issues`.

## Finishing

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version functional-requirements`
2. Write `design-docs/<id>/functional-requirements/v<version>.md` (from the
   template) and `design-docs/<id>/functional-requirements/v<version>.data.json`
   (per the schema).
3. Hash the product idea input: `python scripts/pipeline_tool.py --project <id> latest product-idea`
   (use its `hash` and `version` in your envelope's `inputs_consumed`).
4. Validate your own data file before finalizing:
   `python scripts/pipeline_tool.py --project <id> validate-data functional-requirements --path design-docs/<id>/functional-requirements/v<version>.data.json`
   — fix any reported errors before proceeding.
5. Write the envelope to `design-docs/<id>/functional-requirements/v<version>.envelope.json`
   per `references/pipeline-conventions.md`'s schema, mapping your
   Completeness Assessment status to the envelope `status` per that doc's
   mapping table, with `"next_skill": "non-functional-requirements"`.
6. Run `python scripts/pipeline_tool.py --project <id> finalize design-docs/<id>/functional-requirements/v<version>.envelope.json`
7. Report to the user: the project ID (if this was newly minted, remind
   them to save it), the version produced, a short summary, and — if
   status is READY — that `non-functional-requirements` can now run.

Your final output to the user/orchestrator is the document, the data file,
and the envelope. Don't narrate your reasoning process as part of the
deliverable.
