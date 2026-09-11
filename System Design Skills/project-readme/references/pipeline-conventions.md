# Design pipeline conventions

These conventions are shared by all eight pipeline skills: `mini-prd`,
`functional-requirements`, `non-functional-requirements`,
`architecture-design`, `mermaid-js`, `project-readme`, `sprint-planning`,
and `design-pipeline-orchestrator`. Every skill uses the same
`pipeline_tool.py` (a copy lives in each skill's `scripts/` folder) and
the same seven JSON Schemas (copies live in each content skill's `schema/`
folder), so behavior is identical no matter which skill is invoked.

The core pipeline is: **mini-prd → functional-requirements →
non-functional-requirements → architecture-design → mermaid-js →
project-readme**. mini-prd is the only stage with no upstream document to
gate on — it starts from a raw problem/idea description instead.
project-readme is the pipeline's true final stage, run automatically
after mermaid-js as part of the normal cascade (unlike sprint-planning,
below).

`sprint-planning` sits outside that cascade: once functional-requirements,
non-functional-requirements, and architecture-design are all `READY`, it
can be invoked — independently, on request, once per sprint — to turn the
design into implementation tasks. See "Sprints and task tracking" below.

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

A project's unique ID is a two-word string (e.g. `curious-mango`), minted
by `pipeline_tool.py` — never invented or guessed by a skill or by you.
Before running any other `pipeline_tool.py` command, in every skill in
this pipeline (including the orchestrator), work out the project ID like
this:

1. **Check whether the user already gave you one** in their current
   message or earlier in this conversation (it looks like
   `word-word`). If so, skip to step 3.
2. **Otherwise, ask.** Something like: *"Is this a new project, do you
   have an existing project ID (looks like `curious-mango`), or do you
   have the path to an existing project's documents? If it's new, what
   should I call it — a short name like 'url-shortener' is fine — and
   where would you like the documents saved? (If you don't have a
   preference, I'll create it right here in the current working
   directory.)"*
   - **New project:** you now need both a name (optional) and a location
     (required to ask about, even though a default exists — see below).
     Run `python scripts/pipeline_tool.py resolve-project --name "<short name>" --location "<path>"`
     with no `--project` (omit `--name` if the user didn't give one; omit
     `--location` only if the user explicitly said to use the default —
     see below). It mints an ID, creates the project's folder there (see
     "Where documents live" below), and registers it. Tell the user the
     new ID and that they'll need it to resume this project later (they
     might want to save it somewhere) — the folder path alone won't help
     them resume through the ID lookup, since that's step 3's path, not
     this one.
   - **Existing project — user gives you an ID:** go to step 3.
   - **Existing project — user gives you a path instead of an ID** (e.g.
     they copied the folder from another machine, or don't have the ID
     handy but know where the documents live): go to step 4.
   - **User doesn't remember their ID or the path:** run
     `python scripts/pipeline_tool.py list-projects` and show them the
     list (name + ID + path) to jog their memory, rather than guessing
     which one they mean.
3. **Confirm an existing ID before trusting it:**
   `python scripts/pipeline_tool.py resolve-project --project <id>`.
   - `EXISTING` → use it for the rest of this session.
   - `PROJECT_NOT_FOUND` → tell the user plainly that ID doesn't exist.
     Ask whether they mistyped it (offer `list-projects`), have a path
     instead (go to step 4), or actually want to start a new project.
     Don't silently fall back to minting a new ID without asking — that
     would silently orphan whatever they thought they were resuming.
4. **Adopt an existing folder by path**, when the user gives you a path
   instead of (or after failing to confirm) an ID:
   `python scripts/pipeline_tool.py resolve-project --path "<path>"`.
   - `EXISTING` → that path is already registered; use the `project_id`
     it returns.
   - `ADOPTED` → the folder existed but wasn't registered (lost registry,
     copied from another machine, etc.) and looks like it actually
     contains pipeline documents. It's now registered under the returned
     `project_id` — **tell the user this ID**, especially if
     `id_inferred_from_folder_name` is `false` (meaning the ID couldn't be
     read from the folder name and a fresh one was minted instead, so it
     won't match anything they remember from before).
   - `ADOPTED_EMPTY` → the folder was registered, but it doesn't contain
     any recognizable pipeline structure (no `functional-requirements/`,
     etc.). Flag this to the user rather than silently proceeding — it's
     probably the wrong path, or a genuinely brand-new, empty folder they
     pointed you at on purpose.
   - `PATH_NOT_FOUND` → tell the user plainly and ask for a corrected path
     or a project ID instead.

Once you have a confirmed project ID, pass it as `--project <id>` on
every subsequent `pipeline_tool.py` call in this session — the path
itself is only ever used at this resolution step, never passed to any
other command. A project ID being already present is exactly what tells
you this is a returning project — check `plan` next to see what, if
anything, needs to run to bring it up to date; don't assume the user
wants everything regenerated just because they came back.

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

## Where documents live

**The location is something the user is asked about when creating a new
project — never decided silently, and there's no hardcoded absolute
fallback.** See "Getting the project ID" above for the exact question.
Documents are never written inside the skills installation directory,
and never silently nested inside a generic subfolder like `design-docs/`
— but unlike earlier versions of this pipeline, there's no fixed system
path (home directory, `C:\`, an environment variable) baked in either.

Each project gets its own folder, `<slug>-<unique-id>/`, created under
whichever location the user specified via `--location` on
`resolve-project`. `<slug>` comes from the short project name you asked
the user for (e.g. "URL Shortener" → `url-shortener`); `<unique-id>` is
the minted ID (e.g. `curious-mango`). If the user didn't give a name, the
slug falls back to `project`. So a typical project folder might look like
`~/my-projects/url-shortener-curious-mango/` if the user chose that
location.

**If the user has no location preference, the fallback is the current
working directory** — wherever `pipeline_tool.py` is actually being run
from — not a system-wide default. This makes the fallback
workspace-relative: a project created with no `--location` from inside
one working directory (e.g. a repo you're already in) stays associated
with that directory, similar to how a `.git` folder works. This applies
to the project's registry entry too, not just its files — see the note
below.

`pipeline_tool.py` resolves the exact path for you — you never construct
it by hand. `resolve-project` returns it as `path` in its JSON output
(along with `location_source`: `"user-specified"` or `"default"`, so you
know which happened and can report it accurately); the same `path` value
comes back from every other command's output wherever a path is reported
(`latest`, `next-version`, `check-ready`). When writing a new document,
build its path from that project root: `<project-root>/<doc-type>/vX.Y.md`.

**Important consequence of the cwd fallback:** the project registry
itself (see below) also resolves relative to the current working
directory when no `--location` was given at creation time — it isn't a
single global list. Practically: a project created with no `--location`
is only discoverable (`list-projects`, resuming by `--project <id>`) from
the same working directory it was created in. If a command reports a
project ID as not found, and the user is confident the ID is right,
check whether they might be in a different working directory than when
it was created — that's the first thing to ask about, not a sign the
project was lost.

Inside a project's folder, the layout is:

```
<project-root>/                          e.g. ./url-shortener-curious-mango/
  product-idea/
    current.md
    LATEST.json            # {"version", "hash", "doc_path"}
  mini-prd/
    v1.0.md
    v1.0.data.json
    v1.0.envelope.json
    LATEST.json            # {"version","status","doc_path","data_path","envelope_path","hash"}
  functional-requirements/  (same shape)
  non-functional-requirements/   (same shape)
  architecture-design/           (same shape)
  mermaid-diagrams/
    v1.0/                  # directory: 01-request-flow.mmd, index.md, ...
    v1.0.data.json
    v1.0.envelope.json
    LATEST.json            # doc_path points at the v1.0/ directory
  project-readme/          (same shape as mini-prd — versioned .md + .data.json)
  README.md                # unversioned convenience copy of project-readme's
                            # latest .md, kept at the project root for visibility
  sprints/                 # only if sprint-planning has been run — see below
```

Separately, a small registry at `<current-working-directory>/.design-pipeline/projects.json`
maps every project's unique ID to its folder and name — this is what
`resolve-project` and `list-projects` read and write. You don't need to
touch this file directly; it's internal bookkeeping, not a document.

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
which they should always be for the five content stages), computes the
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
  "document_path": "<project-root>/functional-requirements/v1.1.md",
  "data_path": "<project-root>/functional-requirements/v1.1.data.json",
  "inputs_consumed": {
    "mini-prd": {"version": "1.1", "hash": "sha256:..."}
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
| `READY_FOR_NFR` / `READY` (mermaid-diagrams, project-readme) | `READY` |
| `READY_FOR_IMPLEMENTATION_PLANNING` / `READY_WITH_ASSUMPTIONS` (architecture-design only) | `READY` |
| `BLOCKED` (mini-prd, functional-requirements, non-functional-requirements — with blocking issues listed) | `BLOCKED_QUESTION` |
| `BLOCKED` (architecture-design only — per its own definition, this specifically means an unresolved material contradiction, not just missing information; see architecture-design's own SKILL.md) | `CONFLICT` |
| A run that failed before producing a real document at all (e.g. an unreadable input) | `ERROR` |

Note architecture-design's status names differ from every other stage's
(`READY_FOR_IMPLEMENTATION_PLANNING` / `READY_WITH_ASSUMPTIONS` / `BLOCKED`
instead of `READY_FOR_<NEXT_STAGE>` / `BLOCKED`) — this is deliberate,
matching the architecture profession's own terminology rather than
forcing every stage into identical naming. `READY_WITH_ASSUMPTIONS` is
architecture-design's normal, common outcome, not a degraded one — most
real architectures proceed with some explicit assumptions rather than
none.

## Reading inputs (every skill except mini-prd)

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

## Working in MVP-sized batches

The pipeline doesn't try to fully specify a product in one pass. Every
content-producing document **except mini-prd** carries an `mvp` object in
its `data.json` (mini-prd's own "MVP Scope" section — In Scope / Out of
Scope — is a single upfront product-level decision, not a batch-
progression object; see mini-prd's own SKILL.md for why the two shouldn't
be conflated):

```json
"mvp": {
  "number": 1,
  "new_in_this_mvp": 9,
  "total_included": 9,
  "is_final": false,
  "deferred": ["Bulk link import", "Custom domains"]
}
```

(`new_in_this_mvp`/`total_included`/`deferred` apply to
functional-requirements and non-functional-requirements, which hold a
growing list of items; architecture-design and mermaid-diagrams carry only
`number` and `is_final`, since they describe a design rather than a count
of items.)

**`mvp.number` is not the same thing as `version`.** `version` bumps on
*every* approved change to a document, whether that change is "add the
next batch of new scope" or just "fix the wording of an existing item."
`mvp.number` only advances on the former — a wording fix to something
already approved keeps the same `mvp.number` as before, even though it
still gets a new `version`.

**The ~10-item batch size is enforced, not just suggested.**
`new_in_this_mvp` is schema-capped at 12 (functional-requirements) — a
skill that tries to add more than that in one round has its `finalize`
call rejected. This exists to catch a skill (or a large idea) dumping
everything into one round; genuinely large scopes should be split across
more MVPs, not one oversized one.

**`is_final` propagates downstream.** functional-requirements decides it
first (nothing meaningful left to defer); non-functional-requirements and
architecture-design set their own `is_final` to true only once *all* their
inputs also say `is_final: true`; mermaid-diagrams just carries whatever
architecture-design said. This is what lets the orchestrator know, once a
full cycle finishes, whether to offer another MVP or say the design is
complete.

**Architecture-design cross-checks `mvp.number` between its two inputs**
before designing anything — if functional-requirements is on MVP 2 but
non-functional-requirements is still on MVP 1, that's a sign NFR hasn't
caught up yet, not something to design around by mixing scopes.

## The backlog: where deferred items actually live

A document's `deferred` array (in functional-requirements' and
non-functional-requirements' `data.json`) is just a snapshot — what was
deferred *as of that version*. The living, persistent list is a separate
per-doc-type file, `<project-root>/<doc-type>/backlog.json`, managed
through its own commands rather than being part of any document:

```
python scripts/pipeline_tool.py --project <id> backlog-add <doc-type> --text "..." --source skill|user
python scripts/pipeline_tool.py --project <id> backlog-list <doc-type> [--all]
python scripts/pipeline_tool.py --project <id> backlog-resolve <doc-type> --id BL-N --status included|dropped [--resulting-id FR-013]
```

Each item is `{"id": "BL-N", "text", "source", "status", "added_at"}`,
optionally `"resulting_id"` once resolved. This isn't schema-validated
like a document — it's tool-managed state, the same category as
`LATEST.json`, not a pipeline document with its own contract.

Two things this enables:

1. **The skill suggests, the user decides.** When a round identifies more
   good candidates than fit in this MVP, they go on the backlog via
   `backlog-add ... --source skill` — and the skill surfaces them by name
   during its human review checkpoint (not just a passing mention), so the
   user can pull one into this round instead of leaving it for later.
2. **The user can add to the backlog directly**, any time, without
   triggering a full document regeneration: `backlog-add ... --source
   user`. This is a lightweight operation — it doesn't touch any finalized
   document or bump a version, so it doesn't need the human review
   checkpoint that a real document revision does.

When starting a new MVP round, a skill reads `backlog-list <doc-type>`
*first*, before deriving anything new — the backlog is the starting
candidate pool, not an afterthought. Items that make it into this round
get `backlog-resolve ... --status included --resulting-id <the real ID>`;
items that come up again but still don't fit stay pending; anything newly
identified as out-of-scope this round gets added fresh.

## Conflict detection (architecture-design, but relevant to any skill that consumes multiple inputs)

If two required inputs make contradictory claims (e.g., an FR implying a
scale the NFR document doesn't support, or vice versa), do not silently
pick one. Set the document's own Completeness Assessment status to
`CONFLICT`, the envelope's `status` to `CONFLICT`, one `errors` entry per
contradiction with `code: "CONFLICT_DETECTED"`, and a `summary` describing
the mismatch in plain language. Still write and finalize a document — a
short conflict report is a legitimate, useful pipeline output; a design
built on an unresolved contradiction is not.

## Discovering what exists, without hardcoding a doc-type list

`list-doc-types` returns every document type a project actually has
(anything with a `LATEST.json`, including `sprints/sprint-NN` entries),
each with its current version and status:

```
python scripts/pipeline_tool.py --project <id> list-doc-types
```

This is what `project-readme` uses to build its document index — and it's
generally the right tool any time a skill needs to know what's present
rather than assuming a fixed list, since not every project has run
`sprint-planning`, and the set of documents only grows over the life of a
project.

## Sprints and task tracking (sprint-planning only)

Sprint documents don't fit the "one fixed doc_type, growing/cumulative"
pattern the other stages use — each sprint is a new, non-overlapping unit
of up to 10 tasks, created independently on request. They use **dynamic
doc types**: `sprints/sprint-01`, `sprints/sprint-02`, and so on, all
validated against one shared `schema/sprint.schema.json` regardless of
number. Every generic command (`latest`, `check-ready`, `next-version`,
`validate-data`, `finalize`, `hash-file`) already works with these
doc-type strings exactly like any other — you don't need special-cased
commands to read or write a sprint's `.md`/`.data.json`/`.envelope.json`.

Two things ARE sprint-specific:

- **`next-sprint`** — finds the next sprint number (highest existing
  finalized sprint + 1, or 1 if none), and reports the previous sprint's
  paths and which of its tasks aren't yet `DONE`. Use this instead of
  `next-version` to find *which* sprint you're writing; still use
  `next-version <that sprint's doc_type>` to get the version number
  within it.
- **Task status tracking** — each task's lifecycle
  (`NOT_READY`/`READY`/`IN_PROGRESS`/`DONE`) lives in a separate,
  deliberately mutable `status.json` per sprint, not in the versioned
  document itself (status changes constantly as work happens; the plan's
  *content* shouldn't churn a version bump every time someone starts or
  finishes a task). Three commands manage it:

  ```
  python scripts/pipeline_tool.py --project <id> task-status-init <doc_type> --path <data.json path>
  python scripts/pipeline_tool.py --project <id> task-status-set <doc_type> --id TASK-NNN --status DONE
  python scripts/pipeline_tool.py --project <id> task-status-list <doc_type>
  ```

  `task-status-init` seeds every task's initial status from its
  `prerequisites` array (checking prerequisite completion **across every
  sprint**, not just the current one — a task in Sprint 2 can depend on a
  Sprint 1 task). `task-status-set ... --status DONE` automatically
  cascades: it re-checks every task in every sprint whose prerequisites
  include the one just completed, and flips any that are now fully
  satisfied from `NOT_READY` to `READY`. Never hand-compute which tasks
  unblock — trust the cascade, then `task-status-list` to see the result.

## What the orchestrator does that individual skills don't

Individual skills only check their *own* required inputs and only produce
*their own* document. Deciding which skills need to run at all — including
cascading re-runs when an upstream document changes — is the
orchestrator's job (`design-pipeline-orchestrator`), via
`pipeline_tool.py plan`. A skill should never invoke another skill itself.
