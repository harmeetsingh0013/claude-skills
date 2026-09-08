---
name: non-functional-requirements
description: Produces a versioned Non-Functional Requirements Document (with a machine-readable data contract covering performance, scalability, availability, security, and other quality attributes) from a Functional Requirements Document, as stage 2 of a four-stage design pipeline (functional-requirements → non-functional-requirements → architecture-design → mermaid-js). Use this when the user wants to define quality attributes, constraints, SLAs, throughput/latency targets, or non-functional requirements for a product that already has (or should have) a functional requirements document, or explicitly asks to run/update the "non-functional requirements" / "NFR" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. Do not use this to make architecture or technology decisions (e.g. "use S3", "use Postgres") — those belong to architecture-design.
---

# Non-Functional Requirements

You own **how well the system must perform, under what constraints, and
with what quality attributes** — not how it's built. Read
`references/pipeline-conventions.md` once at the start of a session if you
haven't already.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID, otherwise ask the user whether it's new
or existing, then confirm via `resolve-project`). This skill is never the
first stage run for a brand-new project (functional-requirements always
runs first), so you should normally be *confirming* an ID the user already
has rather than minting one — if the user seems to be starting completely
fresh with no FR document yet, that's a sign to point them at
`functional-requirements` (or the orchestrator) instead. Every
`pipeline_tool.py` call below assumes a confirmed `--project <id>`, placed
**before** the subcommand.

## Input gate

```
python scripts/pipeline_tool.py --project <id> check-ready functional-requirements
```

If this exits non-zero, stop immediately and report the exact message —
something like: `ERROR: Functional Requirements Document is required.`
Do not attempt to reconstruct functional requirements from memory or from
earlier conversation, and don't start interviewing the user about the
product from scratch. The gate exists precisely so this skill never
free-floats without a grounded FR document to derive quality attributes
from.

If it succeeds, load both the `.md` and `.data.json` at the paths it
printed, then run:

```
python scripts/pipeline_tool.py --project <id> validate-data functional-requirements
```

Record the `PASS`/`FAIL` result in your own document's "Input validation"
field. A `FAIL` here means the upstream data contract is structurally
broken even though its status claimed READY — treat that as a blocking
condition and don't proceed to generate NFRs against it; report it instead.

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version non-functional-requirements`.
If it returns a `previous_doc_path`/`previous_data_path`, read both as your
baseline. Update only the quality attributes affected by whatever changed
upstream (new/changed FRs, or a constraint the user just gave you) — don't
regenerate attributes that are still accurate, and don't renumber existing
NFR-N IDs.

## How to derive NFRs from FRs

For each functional requirement (read them from the FR `.data.json`'s
`requirements` array, not just the prose), ask what quality attributes it
implies, and discover concrete values for them — a number, a range, or an
explicit "not specified, assumed X" — rather than a vague adjective. If an
FR says "Users can upload videos," don't stop at "uploads should be fast."
Work out:

- maximum file size / video length
- supported formats
- upload throughput and concurrent upload limits
- upload latency and processing latency targets
- availability target for the upload path
- storage durability and retention requirements
- privacy and access-control expectations
- security requirements (encryption in transit/at rest, auth strength)
- geographic/data-residency requirements, if relevant

This list is illustrative, not exhaustive — the actual attributes that
matter depend on what the FRs describe. Cover the categories in
`references/nfr-checklist.md` as a prompt for what to consider, but only
include what's actually relevant to this product's FRs. Every NFR you
write should record which FR-N(s) motivated it (the template's `Related
FR` field, and `data.json`'s `related_fr` array) — an NFR with no traceable
FR is a sign you've invented a requirement rather than derived one.

## Scope discipline

A non-functional requirement constrains a measurable property of the
system's behavior. It never names a specific product, vendor, or
technology. If you write "Use S3 for storage," stop — rewrite it as the
durability/availability/cost constraint that made S3 seem appealing, and
let architecture-design pick the technology.

- Good: "Uploaded video must be durably stored with 99.999999999%
  annual durability."
- Not this: "Store uploaded video in Amazon S3."

## No hallucination

Where a concrete number genuinely can't be inferred or reasonably assumed
from the FR document or general domain norms, don't invent one. List it in
"NFR Open Questions" tied to the relevant FR-N, and set the Completeness
Assessment to `BLOCKED`. A missing throughput number is a legitimate gap; a
made-up one is a liability the architecture stage will silently build on.

## Document structure

Fill in `templates/non-functional-requirements.md` exactly, including the
"Functional Requirements Input" section (input document version + your
`validate-data` result) near the top. See `examples/url-shortener-nfr.md`
for a fully worked excerpt plus its matching `data.json`.

Alongside the `.md`, produce a `.data.json` following
`schema/non-functional-requirements.schema.json` — this is the contract
`architecture-design` will read.

## Completeness Assessment

```
Non-functional requirements status:
READY_FOR_ARCHITECTURE
```

or

```
Non-functional requirements status:
BLOCKED

Blocking issues:
- NFR-012 requires a concrete number the FR document doesn't imply and the
  user hasn't provided ...
```

Set the same value in `data.json`'s `status` field
(`READY_FOR_ARCHITECTURE` or `BLOCKED`), and list the same issues in
`blocking_issues`.

## Human review checkpoint — before writing anything to disk

Quality-attribute numbers you've derived or assumed are exactly the kind
of thing a user will want to sanity-check — a latency target, a
compliance requirement, or an availability number you inferred might not
match what they actually need.

Draft the full document (and your intended Completeness Assessment)
**directly in your response**, not to disk yet. Then explicitly ask
something like: *"Here are the non-functional requirements derived from
your FR document. Do these targets and constraints look right, and is
there anything missing — a compliance requirement, a specific SLA, a
constraint I should know about? If this looks good, I'll lock it in as
v\<version\> and move on to architecture design."* Stop and wait for their
reply in a new turn — don't write files or finalize in the same turn you
present the draft.

If they ask for changes, revise and ask again. Repeat until the user
explicitly confirms this version, or explicitly tells you to proceed
without further review. This applies even when the orchestrator invoked
you — it decides *which* stages run, not whether this stage's content is
correct.

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version non-functional-requirements`
2. Write `design-docs/<id>/non-functional-requirements/v<version>.md` and
   `design-docs/<id>/non-functional-requirements/v<version>.data.json`.
3. Record `inputs_consumed`: the `functional-requirements` version + hash
   from the `check-ready` output above.
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data non-functional-requirements --path design-docs/<id>/non-functional-requirements/v<version>.data.json`
5. Write the envelope to `design-docs/<id>/non-functional-requirements/v<version>.envelope.json`,
   mapping your Completeness Assessment status per
   `references/pipeline-conventions.md`'s table, with
   `"next_skill": "architecture-design"`.
6. Run `python scripts/pipeline_tool.py --project <id> finalize design-docs/<id>/non-functional-requirements/v<version>.envelope.json`
7. Report to the user the version produced, a short summary, and whether
   `architecture-design` can now run — report this even if the
   orchestrator invoked you, rather than silently continuing.
