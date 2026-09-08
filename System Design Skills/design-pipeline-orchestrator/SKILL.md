---
name: design-pipeline-orchestrator
description: Coordinates the four-stage design pipeline (functional-requirements → non-functional-requirements → architecture-design → mermaid-js), deciding which stages need to run or re-run given a new or changed product idea, and enforcing that a stage never runs on stale or non-READY input. Use this whenever the user wants to run the whole pipeline end-to-end, wants to know pipeline status, gives a new product idea intending the full pipeline, or changes an upstream input (product idea, an FR, an NFR constraint) and wants downstream documents kept in sync. Use this INSTEAD of invoking an individual pipeline skill directly whenever more than one stage might be affected, or whenever it's unclear which stage(s) need to run. If the user asks specifically and only for one stage by name with no ambiguity about staleness, the individual skill (functional-requirements / non-functional-requirements / architecture-design / mermaid-js) can be used directly.
---

# Design Pipeline Orchestrator

You decide *which* pipeline skills need to run and in *what order* — you do
not write requirements, architecture, or diagrams yourself. Each stage's
actual content is produced by following that stage's own skill
(`functional-requirements`, `non-functional-requirements`,
`architecture-design`, `mermaid-js`), which you should treat as available
sub-skills to consult, the same way you'd consult any other skill. Read
`references/pipeline-conventions.md` once at the start of a session if you
haven't already — it defines the project-ID scheme, the shared directory
layout, the two-file document contract (`.md` + `.data.json`), and the
envelope schema that make this coordination possible.

## Step 1: Get the project ID — always, before anything else

This is the very first thing to resolve, whether the user is starting a
brand-new product or coming back to continue one. A project ID being
present or absent is itself the signal that tells you which case you're
in — that's the whole point of asking:

1. **Check whether the user already gave you one** in their current
   message (looks like `word-word`, e.g. `curious-mango`). If so, skip to
   step 3.
2. **Otherwise, ask:** *"Is this a new project, or do you have an existing
   project ID?"*
   - **New:** `python scripts/pipeline_tool.py resolve-project` (no
     `--project`). This mints an ID and creates its folder — tell the user
     the new ID and that they should hang onto it to resume later.
   - **Existing, but they don't remember the exact ID:** run
     `python scripts/pipeline_tool.py list-projects` and show them the
     list rather than guessing.
3. **If they gave you an ID, confirm it before trusting it:**
   `python scripts/pipeline_tool.py resolve-project --project <id>`.
   - `EXISTING` → this is a returning project; proceed to Step 2 below,
     which will naturally figure out what (if anything) needs to run to
     bring it up to date — don't assume everything needs regenerating.
   - `PROJECT_NOT_FOUND` → tell the user plainly, and ask whether they
     mistyped it or actually want to start fresh. Don't silently mint a
     new ID as a fallback.

Every `pipeline_tool.py` call for the rest of this run uses
`--project <id>` (placed **before** the subcommand — see
`references/pipeline-conventions.md`).

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

- New or updated product idea: `echo "<idea>" | python scripts/pipeline_tool.py --project <id> set-idea`
- A change the user describes as an edit to an existing FR or NFR document
  (not a fresh idea) doesn't go through `set-idea` — instead, invoke the
  relevant stage's skill directly with the user's requested change in mind;
  that skill will read its own previous version (`.md` and `.data.json`) as
  a baseline and produce the next version itself. Only `set-idea`
  represents a change at the very top of the pipeline.

## Step 4: Compute the plan

```
python scripts/pipeline_tool.py --project <id> plan
```

This walks all four stages in order and reports, per stage, one of:

- `RUN` — this stage's recorded inputs no longer match its required
  inputs' current versions (or it has never been run, or its current
  version isn't READY). Invoke that stage's skill.
- `SKIP` — up to date; do not re-run it, and use its existing version as
  the input for whatever comes next.
- `BLOCKED` — a required input doesn't exist yet or isn't READY. Don't
  invoke this stage; work through the stages it's waiting on first (they
  should appear earlier in the plan).

The plan already accounts for cascading: if `functional-requirements`
needs to run, everything downstream of it will show `RUN` too once you
re-run the plan after FR completes, because their recorded input hash will
then be stale relative to the new FR version. You don't need to manually
figure out the downstream blast radius — just work through the plan in
order and re-check it as you go (see Step 5).

## Step 5: Execute the plan, one stage at a time — and stop between every stage

For each stage marked `RUN`, in the order the plan lists them
(functional-requirements, then non-functional-requirements, then
architecture-design, then mermaid-js):

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
   *"Functional requirements are locked at v1.0. Ready for me to continue
   with non-functional requirements, or would you like to pause here?"*
   Wait for their answer before invoking the next stage — don't chain
   straight through the whole plan in one uninterrupted sequence. This
   gives the user control over pacing, not just content, and a natural
   place to stop if they want to think something over.
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

## Step 6: Report status

After the run (whether it completed fully or stopped on an issue), give the
user a short summary: the project ID (again, if newly minted), which
stages ran and to what version, which were skipped as up to date, and — if
execution stopped early — exactly what's blocking and what input would
unblock it.

## Answering "what's the pipeline status?" without changing anything

If the user just wants to know where things stand, resolve the project ID
per Step 1, then run `python scripts/pipeline_tool.py --project <id> plan`
and `latest <doc_type>` for each stage, and report it — don't invoke any
stage skill just to answer a status question. If the user asks what
projects exist at all, `list-projects` answers that directly.
