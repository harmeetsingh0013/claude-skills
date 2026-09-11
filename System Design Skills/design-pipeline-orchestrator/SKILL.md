---
name: design-pipeline-orchestrator
description: Coordinates the six-stage design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js → project-readme), deciding which stages need to run or re-run, and enforcing that a stage never runs on stale or non-READY input. The pipeline works in MVP-sized iterations — each requirements stage produces a small batch (~10 items) per round, not the whole product at once — and this skill tracks when an MVP is complete and offers to start the next. Use this to run the pipeline end-to-end, check status, start a new product, begin the next MVP, or propagate a changed input downstream. Prefer this over invoking an individual stage directly whenever more than one stage might be affected or it's unclear which should run; use a specific stage skill (mini-prd / functional-requirements / non-functional-requirements / architecture-design / mermaid-js / project-readme) only when the user names exactly one with no staleness ambiguity.
---

# Design Pipeline Orchestrator

You decide *which* pipeline skills need to run and in *what order* — you do
not write the PRD, requirements, architecture, or diagrams yourself. Each
stage's actual content is produced by following that stage's own skill
(`mini-prd`, `functional-requirements`, `non-functional-requirements`,
`architecture-design`, `mermaid-js`, `project-readme`), which you should
treat as available sub-skills to consult, the same way you'd consult any
other skill. Read `references/pipeline-conventions.md` once at the start
of a session if you haven't already — it defines the project-ID scheme,
the shared directory layout, the two-file document contract (`.md` +
`.data.json`), and the envelope schema that make this coordination
possible.

## Step 1: Get the project ID — always, before anything else

This is the very first thing to resolve, whether the user is starting a
brand-new product or coming back to continue one. A project ID being
present or absent is itself the signal that tells you which case you're
in — that's the whole point of asking:

1. **Check whether the user already gave you one** in their current
   message (looks like `word-word`, e.g. `curious-mango`) — or a path to
   an existing project's documents. If they gave an ID, skip to step 3; if
   a path, skip to step 4.
2. **Otherwise, ask:** *"Is this a new project, do you have an existing
   project ID, or do you have the path to an existing project's
   documents? If it's new, what should I call it, and where would you
   like the documents saved — I can use the current working directory if
   you don't have a preference."*
   - **New:** `python scripts/pipeline_tool.py resolve-project --name "<short name>" --location "<path>"`
     (no `--project`; omit `--name` if the user didn't give one; omit
     `--location` only if they explicitly said to use the default). This
     mints an ID, creates its folder at the location they chose (or the
     default), and registers it — tell the user the new ID and where it
     was created, and that they should hang onto the ID to resume later
     (the name alone won't be enough to resume; resuming works through
     the ID).
   - **Existing, but they don't remember the exact ID or a path:** run
     `python scripts/pipeline_tool.py list-projects` and show them the
     list (with names and paths) rather than guessing.
3. **If they gave you an ID, confirm it before trusting it:**
   `python scripts/pipeline_tool.py resolve-project --project <id>`.
   - `EXISTING` → this is a returning project; proceed to Step 2 below,
     which will naturally figure out what (if anything) needs to run to
     bring it up to date — don't assume everything needs regenerating.
   - `PROJECT_NOT_FOUND` → tell the user plainly, and ask whether they
     mistyped it, have a path instead (go to step 4), or actually want to
     start fresh. Don't silently mint a new ID as a fallback.
4. **If they gave you a path instead** (or the ID above wasn't found and
   they have a path handy — e.g. the registry was lost, or this folder was
   copied from another machine): `python scripts/pipeline_tool.py resolve-project --path "<path>"`.
   - `EXISTING` → already registered; use the `project_id` it returns.
   - `ADOPTED` → newly registered from that folder, and it does contain
     real pipeline documents. Tell the user the resulting `project_id` —
     especially if `id_inferred_from_folder_name` is `false`, since that
     means a fresh ID was minted and won't match anything they remember.
   - `ADOPTED_EMPTY` → registered, but the folder doesn't actually contain
     any pipeline documents. Flag this rather than proceeding as if it
     were a normal resume — confirm with the user this is really the
     right path before treating it as an existing project.
   - `PATH_NOT_FOUND` → tell the user plainly and ask for a corrected path
     or an ID instead.

Documents for this project are written to a dedicated project folder —
wherever the user chose, or the current working directory if they had no
preference (see `references/pipeline-conventions.md`). `resolve-project`'s
output includes the exact `path`; you don't need to do anything with it
yourself; each stage skill derives its own file paths from it.

Every `pipeline_tool.py` call for the rest of this run uses
`--project <id>` (placed **before** the subcommand — see
`references/pipeline-conventions.md`). The path itself, if one was given,
is only ever used at this resolution step.

## Why this needs an orchestrator at all

The pipeline's whole value is that a small change (say, editing one NFR
constraint) shouldn't force regenerating everything from scratch, but it
also shouldn't silently leave downstream documents stale. Getting this
right requires comparing content hashes, not vibes — that's what
`pipeline_tool.py` is for. Trust its output over your own sense of "this
probably didn't need to change."

## Step 2: Make sure the pipeline is initialized

```
python scripts/pipeline_tool.py --project <id> init
```

Safe to run every time — it only creates missing folders within this
project's subtree.

## Step 3: Record any new/changed input

- **New product, or a new problem/idea description:** `echo "<description>" | python scripts/pipeline_tool.py --project <id> set-idea`.
  This is mini-prd's input, not functional-requirements' — the pipeline
  now starts with an interview (mini-prd), not straight into requirements.
  A short, even one-line description is fine here; the mini-prd skill's
  interview is what turns it into something usable.
- A change the user describes as an edit to an existing Mini-PRD, FR, or
  NFR document (not a fresh problem description) doesn't go through
  `set-idea` — instead, invoke the relevant stage's skill directly with
  the user's requested change in mind; that skill will read its own
  previous version (`.md` and `.data.json`) as a baseline and produce the
  next version itself. Only `set-idea` represents a change at the very
  top of the pipeline.
- **The user wants to start the next MVP** (see Step 6) — this doesn't go
  through `set-idea` either, since the Mini-PRD usually hasn't changed.
  Invoke `functional-requirements` directly and let it pick the next
  batch (it reads the previous MVP's `data.json` as baseline regardless
  of whether `plan` would say `RUN` or `SKIP` — see the note in Step 4).

## Step 4: Compute the plan

```
python scripts/pipeline_tool.py --project <id> plan
```

This walks all six stages in order and reports, per stage, one of:

- `RUN` — this stage's recorded inputs no longer match its required
  inputs' current versions (or it has never been run, or its current
  version isn't READY). Invoke that stage's skill.
- `SKIP` — up to date; do not re-run it, and use its existing version as
  the input for whatever comes next.
- `BLOCKED` — a required input doesn't exist yet or isn't READY. Don't
  invoke this stage; work through the stages it's waiting on first (they
  should appear earlier in the plan).

The plan already accounts for cascading: if `mini-prd` needs to run,
everything downstream of it will show `RUN` too once you re-run the plan
after it completes, because their recorded input hash will then be stale
relative to the new version. You don't need to manually figure out the
downstream blast radius — just work through the plan in order and
re-check it as you go (see Step 5).

**`plan` only detects staleness from hash changes — it doesn't know about
MVP progression.** If the user asks to start the next MVP and nothing
about the underlying product idea changed, `plan` will report
`functional-requirements` as `SKIP` (nothing's stale). That's correct as
far as hash comparison goes, but it's not what you want here: starting the
next MVP means deliberately invoking `functional-requirements` anyway,
regardless of what `plan` says, and letting it read the previous round's
`data.json` as baseline. Once it produces a new version, `plan` will
correctly show the downstream stages as `RUN` from that point on.

## Step 5: Execute the plan, one stage at a time — and stop between every stage

For each stage marked `RUN`, in the order the plan lists them (mini-prd,
then functional-requirements, then non-functional-requirements, then
architecture-design, then mermaid-js, then project-readme):

1. Invoke that stage by following its own SKILL.md instructions, passing
   along the same project ID.
2. **Every content stage's own SKILL.md includes a human review checkpoint
   that pauses and asks the user about the draft before writing anything
   or finalizing — let that happen.** Don't summarize the draft yourself
   and answer on the user's behalf, don't tell the stage to skip its
   checkpoint, and don't treat something the user said earlier in the
   conversation (e.g. approving the *plan* to run the pipeline) as
   approval of a *specific stage's content* it hasn't shown them yet.
   Orchestrating the pipeline and approving what it produces are different
   things — only the user does the second one.
3. Once the stage finalizes (`status: "READY"`), **stop and check in with
   the user before invoking the next stage**, even though its own
   checkpoint already got their sign-off on the content. Something like:
   *"The Mini-PRD is locked at v1.0. Ready for me to continue with
   functional requirements, or would you like to pause here?"* Wait for
   their answer before invoking the next stage — don't chain straight
   through the whole plan in one uninterrupted sequence. This gives the
   user control over pacing, not just content, and a natural place to stop
   if they want to think something over.
4. Re-run `python scripts/pipeline_tool.py --project <id> plan` before
   moving to the next stage — don't assume the plan you computed at the
   start is still accurate, since a stage's own output determines whether
   the next one actually needs to run (a rerun doesn't always change the
   resulting document's content in a way that matters, though in practice
   a version bump always changes the hash, so downstream stages will
   generally show `RUN` after any upstream `RUN`).
5. If a stage finishes with `status: "ERROR"`, `"CONFLICT"`, or
   `"BLOCKED_QUESTION"` instead of `"READY"`, stop executing the plan.
   Report the issue to the user (surface the envelope's `errors` or
   `blocking_questions` directly — don't paraphrase away the specifics)
   and wait for their input before continuing. Don't route around a
   blocked stage by skipping ahead to the next one; a downstream stage's
   gate will refuse to run on a non-READY input anyway, so pushing forward
   would just produce a second, more confusing error.

Stages marked `SKIP` or `BLOCKED` at the start need no action beyond what's
already been reported. If the user explicitly says something like "run the
whole pipeline end to end without stopping to ask me," you can skip the
per-stage check-in in Step 5.3 — but each stage's own content checkpoint
still happens regardless, since that's about the content being correct,
not about pacing.

## Step 6: Report status — and offer the next MVP if this one just finished

After the run (whether it completed fully or stopped on an issue), give the
user a short summary: the project ID (again, if newly minted), which
stages ran and to what version, which were skipped as up to date, and — if
execution stopped early — exactly what's blocking and what input would
unblock it.

If `project-readme` finished this run with `status: "READY"` (i.e. a full
MVP cycle just completed end to end, including the project's README being
regenerated), check whether there's more work implied: read `is_final`
from the latest `functional-requirements` `data.json` (every requirements/
design stage should agree on this by the time project-readme finishes,
since it's carried through — see each stage's own SKILL.md; mini-prd and
project-readme themselves don't carry an `mvp` object the same way — see
"Working in MVP-sized batches" in `references/pipeline-conventions.md`).

- **`is_final: false`** — there's more scope deferred to future MVPs.
  Check the backlog for a fuller picture than the FR document's `deferred`
  snapshot: `python scripts/pipeline_tool.py --project <id> backlog-list functional-requirements`.
  Tell the user what MVP just shipped (mentioning that `README.md` at the
  project root now reflects it) and what's pending on the backlog, then
  ask something like: *"MVP \<N\> is complete end-to-end, and the project
  README is up to date. On the backlog for next time: \<items\>. Want me
  to start MVP \<N+1\>, and should I just prioritize from the backlog
  myself or is there something specific you want pulled in first?"* If
  they say yes, go back to Step 3 with "the user wants the next MVP" as
  the recorded input, and run the pipeline again from
  `functional-requirements`. You can also mention that `sprint-planning`
  can generate implementation tasks for what's already built, even before
  later MVPs are scoped — it only needs FR, NFR, and architecture-design
  to be READY, not `is_final: true`.
- **`is_final: true`** — nothing's deferred; the product's full scope (as
  currently understood) is built out. Say so plainly rather than asking
  about a next MVP that doesn't exist yet — and mention that the design
  is now complete enough to generate implementation tasks, if they want:
  *"The design is fully built out, and the project README is up to date.
  Want me to generate an implementation sprint from it?"* That's the
  `sprint-planning` skill — invoke it only if they say yes; unlike
  `project-readme` (which runs automatically as part of this cascade),
  `sprint-planning` is a separate, on-request capability this orchestrator
  never chains into automatically.

If `sprint-planning` has been run at some point (check
`python scripts/pipeline_tool.py --project <id> list-doc-types` for any
`sprints/sprint-NN` entries) and this run touched anything upstream of
`project-readme`, mention that re-running `project-readme` will pick up
the new sprint in its document index automatically — you don't need to
do anything special to make that happen beyond letting `project-readme`
run as usual.

Don't ask about the next MVP after a partial run (a stage stopped on
`BLOCKED_QUESTION`/`CONFLICT`/`ERROR`, or the user only asked for one
specific stage) — that question only makes sense right after a complete,
successful cycle.

## Answering "what's the pipeline status?" without changing anything

If the user just wants to know where things stand, resolve the project ID
per Step 1, then run `python scripts/pipeline_tool.py --project <id> plan`
and `latest <doc_type>` for each stage, and report it — don't invoke any
stage skill just to answer a status question. Include the current MVP
number and whether it's final (from `functional-requirements`'s latest
`data.json`) as part of that status. If the user asks what projects exist
at all, `list-projects` answers that directly.
