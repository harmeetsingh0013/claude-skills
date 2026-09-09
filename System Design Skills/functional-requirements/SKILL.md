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
`references/pipeline-conventions.md` has the exact procedure. Since this is
usually the first stage invoked for a brand-new product, you're often the
one asking "new project, existing ID, or a path to existing documents?"
and minting the ID via `resolve-project --name "<short name>"` for a new
one (or `resolve-project --path "<path>"` to adopt an existing folder that
isn't registered yet — see conventions doc). Every `pipeline_tool.py` call
below assumes you've done this and shows `--project <id>` accordingly —
always place it **before** the subcommand.

A project ID being already present when the user starts talking to you is
itself informative: it means you're likely resuming, not starting fresh —
run `plan` (see Finishing) or just proceed with the idea they give you,
which `next-version` will treat as a revision automatically.

Documents for this project live in a dedicated folder outside your working
directory (the user's home directory, or `C:\` on Windows — see
`references/pipeline-conventions.md`), not wherever this session happens
to be running. `resolve-project`'s output includes the exact `path` — hang
onto it for constructing file paths in Finishing.

## Input

The only input is the product idea. There is no upstream document to
validate — this is the one skill in the pipeline with no `check-ready` gate.

- If the user gave you the idea directly in conversation, record it:
  `echo "<idea text>" | python scripts/pipeline_tool.py --project <id> set-idea`
- If a product idea has already been recorded for this project and the
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
`summary`. Also read the previous `data.json`'s `mvp` object — you need
its `number` and `total_included` to work out this round's MVP number and
where FR numbering continues from (see "Work in MVP-sized batches" below).

## Work in MVP-sized batches

Don't enumerate every functional requirement the idea implies in one
shot. A large, fully-specified requirements set up front is harder for
the user to review meaningfully, and it front-loads decisions (priority,
scope) that are easier to make well in smaller batches with real feedback
in between. Instead:

1. **Check the backlog first**: `python scripts/pipeline_tool.py --project <id> backlog-list functional-requirements`.
   Anything pending there is a candidate for this round before you think
   up anything new — items land there because a past round suggested them
   and they didn't fit, or because the user added them directly between
   sessions.
2. **Think through the full scope, privately** — combine the backlog with
   anything new the current idea/conversation implies, so your
   prioritization is informed by the whole picture, not just whatever
   comes to mind first.
3. **Select the ~10 most important requirements for this round** — the
   ones that are foundational (other capabilities depend on them),
   highest priority, or make up a coherent, shippable slice on their own.
   Target 10; treat 12 as a hard ceiling — `finalize` will reject a batch
   larger than that (`mvp.new_in_this_mvp` is schema-capped at 12), so if
   you're tempted to go bigger, that's a sign to split into two rounds
   instead.
4. **Actively suggest what didn't make the cut — don't just silently defer
   it.** For everything else you identified (from the backlog or newly
   thought of), add it to the backlog if it isn't already there:
   `python scripts/pipeline_tool.py --project <id> backlog-add functional-requirements --text "..." --source skill`
   You'll surface this list by name during the human review checkpoint
   below — the point is to give the user a real choice about what's in
   this round, not to bury good ideas in a "deferred" footnote they might
   not read closely.
5. **Number continuously across rounds.** If the previous version's `mvp`
   object shows `total_included: 9`, this round's new requirements start
   at FR-010, not FR-001 — figure out the highest existing FR-N from the
   previous `data.json`'s `requirements` array.
6. **Mark `is_final: true`** only when there's genuinely nothing left
   worth deferring — i.e., the backlog is empty (or everything left in it
   was explicitly dropped) and this round's requirements plus everything
   already included cover what the idea implies. Most first rounds should
   be `is_final: false`.

This applies to every run of this skill, not just the very first one —
"starting a new MVP" and "revising functional-requirements" are the same
operation here, just distinguished by whether you're adding a new batch
(bump `mvp.number`) or correcting something already-approved (same
`mvp.number` as before, since you're not adding new scope). If the user
asks you to fix or reword an existing FR rather than add new ones, that's
the latter case — don't bump the MVP number for a correction.

If the user just wants to add something to the backlog without running a
full round (e.g. "add social login to the backlog for later"), that's a
lightweight operation — `backlog-add ... --source user`, then confirm.
It doesn't touch any finalized document or bump a version, so it doesn't
need the human review checkpoint below.

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
group requirements under `### <Capability>` headings. Fill in the "MVP
Scope" section per "Work in MVP-sized batches" above. See
`examples/url-shortener.md` for a fully worked document (including an
illustration of what a second MVP round looks like) plus its matching
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

Note that `READY_FOR_NFR` means *this MVP's slice is internally
consistent and ready for the next stage* — it does not mean the whole
product's requirements are fully captured. `mvp.is_final` is the separate
field that answers that question; most rounds will be `READY_FOR_NFR` with
`is_final: false`.

## Human review checkpoint — before writing anything to disk

A product idea is rarely complete on its own — the user may have
additional capabilities, edge cases, or actors in mind that the idea as
stated didn't spell out. Don't treat your first draft as final just
because it's internally consistent, and don't leave the backlog as a
buried afterthought — surface it as an active suggestion.

Draft the full document (and your intended Completeness Assessment)
**directly in your response**, not to disk yet. Then explicitly present
both the batch and the backlog, and ask for a decision on both — something
like: *"Here are the top \<N\> functional requirements I'd prioritize for
MVP \<number\> — FR-\<X\> through FR-\<Y\>. I'd also suggest keeping an
eye on these for later (or pulling one into this round instead):
\<backlog items by name\>. Does this batch look right — any swaps,
additions, or backlog items you'd rather include now — before I lock it
in as v\<version\> and move on to non-functional requirements?"* Then stop
and wait for their reply in a new turn — don't write files or finalize in
the same turn you present the draft, and don't treat an earlier "looks
good, continue" from a different part of the conversation as approval for
*this* draft.

If they ask for changes, add requirements, or want to swap a backlog item
in, revise the draft and ask again (swapping a backlog item in means
resolving it — see Finishing — and something else may need to move to the
backlog to stay within the cap). Repeat until the user explicitly confirms
this version, or explicitly tells you to proceed without further review.
Only then move on to Finishing.

This checkpoint applies even when you were invoked by the orchestrator:
the orchestrator decides *which* stages run, but that's not a substitute
for the user's own sign-off on what this stage actually produced.

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version functional-requirements`
2. Write `<project-root>/functional-requirements/v<version>.md` (from the
   template) and `<project-root>/functional-requirements/v<version>.data.json`
   (per the schema) — `<project-root>` is the `path` from Step 1's
   `resolve-project` output. Set the `deferred` field in `data.json` to the
   current pending backlog items' text (after the resolutions in step 3).
3. Resolve the backlog: for every backlog item that made it into this
   round, `backlog-resolve functional-requirements --id BL-N --status
   included --resulting-id FR-0NN`. For anything newly identified as
   out-of-scope this round that isn't already on the backlog, `backlog-add
   ... --source skill` (see "Work in MVP-sized batches"). Leave everything
   else pending.
4. Hash the product idea input: `python scripts/pipeline_tool.py --project <id> latest product-idea`
   (use its `hash` and `version` in your envelope's `inputs_consumed`).
5. Validate your own data file before finalizing:
   `python scripts/pipeline_tool.py --project <id> validate-data functional-requirements --path <project-root>/functional-requirements/v<version>.data.json`
   — fix any reported errors before proceeding.
6. Write the envelope to `<project-root>/functional-requirements/v<version>.envelope.json`
   per `references/pipeline-conventions.md`'s schema, mapping your
   Completeness Assessment status to the envelope `status` per that doc's
   mapping table, with `"next_skill": "non-functional-requirements"`.
7. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/functional-requirements/v<version>.envelope.json`
8. Report to the user: the project ID (if this was newly minted, remind
   them to save it), the version produced, a short summary, and — if
   status is READY — that `non-functional-requirements` can now run. If
   you weren't invoked directly by the user (the orchestrator invoked you),
   still report this back rather than silently continuing — the
   orchestrator's own instructions have it check in with the user before
   moving to the next stage.

Your final output to the user/orchestrator is the document, the data file,
and the envelope. Don't narrate your reasoning process as part of the
deliverable.
