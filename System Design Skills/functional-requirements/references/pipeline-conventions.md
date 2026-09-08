# Design pipeline conventions

These conventions are shared by all five pipeline skills: `functional-requirements`,
`non-functional-requirements`, `architecture-design`, `mermaid-js`, and
`design-pipeline-orchestrator`. Every skill uses the same `pipeline_tool.py`
(a copy lives in each skill's `scripts/` folder) and the same four JSON
Schemas (copies live in each content skill's `schema/` folder), so behavior
is identical no matter which skill is invoked.

## Every command needs a project ID — and it goes *before* the subcommand

`--project <project-id>` is a global option, which means it must come
**before** the subcommand on the command line:

```
python scripts/pipeline_tool.py --project curious-mango plan          # correct
python scripts/pipeline_tool.py plan --project curious-mango          # WRONG — argparse will reject this
```

Every command requires `--project` except `resolve-project` (used to
create or confirm a project ID in the first place) and `list-projects`.

## Getting the project ID: do this before anything else, every time

A project ID is a two-word adjective-food string (e.g. `curious-mango`),
minted by `pipeline_tool.py` — never invented or guessed by a skill or by
you. Before running any other `pipeline_tool.py` command, in every skill
in this pipeline (including the orchestrator), work out the project ID
like this:

1. **Check whether the user already gave you one** in their current
   message or earlier in this conversation (it looks like
   `word-word`). If so, skip to step 3.
2. **Otherwise, ask.** Something like: *"Is this a new project, or do you
   have an existing project ID (looks like `curious-mango`)?"*
   - **New project:** run `python scripts/pipeline_tool.py resolve-project`
     with no `--project`. It mints an ID and creates its directory. Tell
     the user the new ID and that they'll need it to resume this project
     later (they might want to save it somewhere).
   - **Existing project — user gives you an ID:** go to step 3.
   - **User doesn't remember their ID:** run
     `python scripts/pipeline_tool.py list-projects` and show them the
     list to jog their memory, rather than guessing which one they mean.
3. **Confirm an existing ID before trusting it:**
   `python scripts/pipeline_tool.py resolve-project --project <id>`.
   - `EXISTING` → use it for the rest of this session.
   - `PROJECT_NOT_FOUND` → tell the user plainly that ID doesn't exist.
     Ask whether they mistyped it (offer `list-projects`) or actually want
     to start a new project. Don't silently fall back to minting a new ID
     without asking — that would silently orphan whatever they thought
     they were resuming.

Once you have a confirmed project ID, pass it as `--project <id>` on
every subsequent `pipeline_tool.py` call in this session. A project ID
being already present is exactly what tells you this is a returning
project — check `plan` next to see what, if anything, needs to run to
bring it up to date; don't assume the user wants everything regenerated
just because they came back.

## Why a script instead of doing this by hand

Version numbers, content hashes, and "is my input actually ready" checks
must be exact every time, or the pipeline's core promise — safe, targeted
re-runs — breaks silently. `pipeline_tool.py` is the single source of truth
for that bookkeeping. Never hand-write a `LATEST.json` file, compute a
version number by eyeballing the previous one, or eyeball whether a
data.json "looks right" — always go through the script, so a bad guess
can't corrupt the state every other skill relies on.

## Documents are contracts, not just prose

Each stage produces **two files**, not one:

- **`vX.Y.md`** — the full human-readable document, following that stage's
  `templates/<doc-type>.md` structure. This is what a person reads.
- **`vX.Y.data.json`** — a structured summary of the same content
  (metadata, requirement/NFR/ADR/diagram entries, completeness status,
  traceability), validated against `schema/<doc-type>.schema.json`.

The `.data.json` is the actual machine-readable contract between stages.
When you consume an upstream document, read structured fields from its
`.data.json` (requirement IDs, statuses, targets) rather than re-parsing
the prose `.md` — that's what makes the pipeline reliable rather than a
chain of natural-language handoffs. See each skill's `examples/` folder
for a worked `.md` + `.data.json` pair.

**mermaid-diagrams is the one exception**: its `document_path` is a
*directory* of `.mmd` files (plus an `index.md` inside that directory for
human readability), not a single markdown file. `pipeline_tool.py` hashes
directories automatically (`hash_path` / `hash-file` both handle this) —
you don't need to do anything different when calling `finalize`.

## Directory layout

Everything lives under `design-docs/<project-id>/`, so a workspace can
hold many unrelated projects side by side without their versions or
LATEST pointers colliding:

```
design-docs/
  curious-mango/
    product-idea/
      current.md
      LATEST.json            # {"version", "hash", "doc_path"}
    functional-requirements/
      v1.0.md
      v1.0.data.json
      v1.0.envelope.json
      LATEST.json            # {"version","status","doc_path","data_path","envelope_path","hash"}
    non-functional-requirements/   (same shape)
    architecture-design/           (same shape)
    mermaid-diagrams/
      v1.0/                  # directory: 01-request-flow.mmd, index.md, ...
      v1.0.data.json
      v1.0.envelope.json
      LATEST.json            # doc_path points at the v1.0/ directory
  another-project-id/
    ...
```

`pipeline_tool.py` resolves all of this for you once you pass
`--project curious-mango` — you never need to construct these paths by
hand except when writing a new document's `.md`/`.data.json` (see each
skill's own "Finishing" section for the exact path).

Documents are never edited in place. A new version is a new set of files;
`LATEST.json` is the only thing that gets overwritten, and only via
`pipeline_tool.py finalize`.

## The completion envelope

Every skill run ends by writing a JSON envelope alongside its document(s),
then calling:

```
python scripts/pipeline_tool.py --project <id> finalize <path-to-envelope>
```

`finalize` validates the envelope's required fields, validates the
`data_path` file against that doc-type's schema (if both are present —
which they should always be for the four content stages), computes the
document's hash, and updates `LATEST.json`. That's the *only* mechanism
that makes a new version visible to downstream skills or the orchestrator
— a document that exists on disk but was never finalized doesn't count.

```json
{
  "envelope_version": "1.0",
  "skill": "functional-requirements",
  "document_type": "functional-requirements",
  "status": "READY",
  "version": "1.1",
  "document_path": "design-docs/curious-mango/functional-requirements/v1.1.md",
  "data_path": "design-docs/curious-mango/functional-requirements/v1.1.data.json",
  "inputs_consumed": {
    "product-idea": {"version": "1.1", "hash": "sha256:..."}
  },
  "next_skill": "non-functional-requirements",
  "summary": "One paragraph: what this version contains and, if it's a revision, what changed and why.",
  "errors": [],
  "blocking_questions": []
}
```

Field notes:

- **status** — the generic, pipeline-control status. One of `READY`,
  `ERROR`, `BLOCKED_QUESTION`, `CONFLICT`. This is *not* the same string as
  the document's own domain-specific completeness assessment (e.g.
  `READY_FOR_NFR`) — set it FROM that assessment using the mapping table
  below. Only `READY` documents are usable as input by a downstream skill;
  `finalize` still records non-READY runs (so the orchestrator can see
  what went wrong), but a downstream skill's `check-ready` gate will
  refuse to treat any other status as valid input.
- **inputs_consumed** — the *exact* version + hash of every upstream
  document (or the product idea) this run actually used. This is what
  makes targeted re-runs possible. Get the hash with
  `pipeline_tool.py hash-file <path>` — never type a hash by hand.
- **errors** — populate only when status is `ERROR` or `CONFLICT`. Each
  entry is `{"code": "...", "message": "..."}`. Use a `code` value a
  human or the orchestrator can branch on, e.g. `MISSING_INPUT`,
  `CONFLICT_DETECTED`.
- **blocking_questions** — populate only when status is
  `BLOCKED_QUESTION`: things you could not reasonably infer and must ask
  the user before producing a real document. Don't guess and mark READY
  instead — a confidently wrong requirements doc is more expensive
  downstream than a question now.

### Mapping a document's own completeness status to the envelope status

| Document's own "Completeness Assessment" | Envelope `status` |
|---|---|
| `READY_FOR_NFR` / `READY_FOR_ARCHITECTURE` / `READY_FOR_MERMAID` / `READY` (mermaid-diagrams) | `READY` |
| `BLOCKED` (with blocking issues listed) | `BLOCKED_QUESTION` |
| `CONFLICT` (architecture-design only, from a Section 3 contradiction) | `CONFLICT` |
| A run that failed before producing a real document at all (e.g. an unreadable input) | `ERROR` |

## Reading inputs (every skill except functional-requirements)

Before doing any generation work:

1. Run `python scripts/pipeline_tool.py --project <id> check-ready <required-doc-type>`
   for every required input. If it exits non-zero, stop — do not attempt to
   reconstruct the document from memory or from conversation context.
   Report the exact message the script printed.
2. Read both the `.md` (for full context) and `.data.json` (for
   structured fields you'll reference, like specific requirement IDs) at
   the paths `check-ready` printed.
3. Validate the input's data contract explicitly and record the result in
   your own document's "Input validation" field:
   `python scripts/pipeline_tool.py --project <id> validate-data <upstream-doc-type>`
   prints `PASS` or `FAIL` with reasons. This is a stricter, structural
   check on top of `check-ready`'s status gate — `check-ready` only tells
   you the upstream skill *claimed* READY; `validate-data` confirms its
   structured output actually matches the schema.
4. Read the *previous version of your own document type* the same way
   (`pipeline_tool.py --project <id> latest <your-doc-type>`), if one
   exists — this is your baseline for incremental updates. Pass it as the
   "previous version" in your envelope's version bump.

## Versioning

Get your version number by running:

```
python scripts/pipeline_tool.py --project <id> next-version <your-doc-type>
```

This returns `1.0` if no previous version exists, or `previous + 0.1`
otherwise, along with the paths to the previous document, data file, and
envelope so you can use them as a baseline. Never compute this yourself.

## Conflict detection (architecture-design, but relevant to any skill that consumes multiple inputs)

If two required inputs make contradictory claims (e.g., an FR implying a
scale the NFR document doesn't support, or vice versa), do not silently
pick one. Set the document's own Completeness Assessment status to
`CONFLICT`, the envelope's `status` to `CONFLICT`, one `errors` entry per
contradiction with `code: "CONFLICT_DETECTED"`, and a `summary` describing
the mismatch in plain language. Still write and finalize a document — a
short conflict report is a legitimate, useful pipeline output; a design
built on an unresolved contradiction is not.

## What the orchestrator does that individual skills don't

Individual skills only check their *own* required inputs and only produce
*their own* document. Deciding which skills need to run at all — including
cascading re-runs when an upstream document changes — is the
orchestrator's job (`design-pipeline-orchestrator`), via
`pipeline_tool.py plan`. A skill should never invoke another skill itself.
