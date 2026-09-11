---
name: mermaid-js
description: Generates Mermaid.js diagram files by reading a Final Architecture Design Document's structured content directly — System Context, Architecture Overview, Component Architecture, Request Flows, Data Model, and Deployment Architecture — and deciding which diagrams that content actually warrants, as stage 4 of a six-stage design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js → project-readme). Use this when the user wants diagrams (component, sequence, ER, deployment, event flow, etc.) generated from an already-completed architecture design, or explicitly asks to run/update the "mermaid" / "diagrams" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. This skill only visualizes an existing, already-decided design — it never makes or reconsiders architecture decisions; if the architecture document's content is too ambiguous to render faithfully, that's a gap to flag, not a decision to make here.
---

# Mermaid.js Diagram Generation

Your job is **extraction, not redesign**. The architecture is already
decided; you translate it into pictures. If you find yourself thinking "I
think a queue would be better here," stop — that thought belongs to
architecture-design, three stages ago, not to you. architecture-design
never hands you a list of diagrams to produce — **you decide what to draw
by reading its actual content** (see "Deriving diagrams from content"
below), and every diagram you produce should be traceable to a specific
section of that document. Read `references/pipeline-conventions.md` once
at the start of a session if you haven't already.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID or a path to existing documents,
otherwise ask the user whether it's new/existing/a path, then confirm via
`resolve-project`). This skill is never the
first stage run for a brand-new project, so you should normally be
*confirming* an ID the user already has. Every `pipeline_tool.py` call
below assumes a confirmed `--project <id>`, placed **before** the
subcommand, and its `path` (documents live in a dedicated folder
wherever the user chose when the project was created — see
`references/pipeline-conventions.md` — the current working directory
only if the user had no preference).

## Input gate

```
python scripts/pipeline_tool.py --project <id> check-ready architecture-design
```

If this fails, stop and report the message — don't try to diagram a design
that doesn't exist yet or isn't READY. If it succeeds, load both the `.md`
and `.data.json` at the paths it printed, then:

```
python scripts/pipeline_tool.py --project <id> validate-data architecture-design
```

Read the architecture document's `mvp.number` too — set your own `mvp`
object to match it. Since this stage only extracts what architecture
already decided, there's no independent MVP judgment to make here; you're
just carrying the label through.

## Deriving diagrams from content — there is no spec list to read

architecture-design's document has no diagram specification section by
design (see its own SKILL.md) — it describes the system in structured
prose and data, and diagramming what's architecturally significant is
this skill's judgment call to make, not something handed to you. Work
through the architecture document's sections and produce a diagram only
where the underlying content is real and non-trivial — skip a diagram
type entirely if the corresponding section is thin, marked "Not
Applicable" (check `not_applicable_sections` in the `.data.json`), or
genuinely doesn't warrant a picture:

- **System context** — from Section 5, if there are external actors or
  dependencies worth showing as a boundary.
- **Container / component architecture** — from Section 6 (Architecture
  Overview) and Section 9 (Component/Service Architecture) — almost
  always warranted unless the system is a single trivial component.
- **Request flow (sequence)** — one per significant flow described in
  Section 10 — only for flows actually described as ordered steps, not
  invented ones.
- **Data model (entity-relationship)** — from Section 12, if there's more
  than one entity or a real relationship to show.
- **Deployment architecture** — from Section 23, if there's redundancy,
  zone/region structure, or a topology worth showing (skip for "deploy
  the container somewhere" with no real structure).
- **Event / messaging flow** — from Section 15, only if messaging
  architecture is actually part of the design (not "Not Applicable").
- **Failure / recovery flow** — from Section 21 (Disaster Recovery) or
  Section 27 (Failure Mode Analysis), only if there's a real recovery
  sequence worth visualizing, not a one-line mitigation.

A simple system might warrant only one or two diagrams (typically
component architecture, maybe one request flow) — that's correct, not
incomplete. Don't manufacture a diagram for every possible type just to
look thorough; that mirrors the same padding architecture-design itself
is instructed to avoid.

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version mermaid-diagrams`.
If a previous version exists, read its directory — keep diagrams
unaffected by the change as-is (same filename, same content), and only
regenerate the ones whose underlying architecture content actually
changed.

## Workflow: detect MCP → use if available → otherwise generate natively → validate → report limitations

1. **Detect.** Check whether an MCP tool for Mermaid diagram generation or
   validation is available in this session (look at your available tools).
2. **Use if available.** If such a tool exists, use it to generate and/or
   validate the diagrams rather than hand-writing Mermaid syntax yourself —
   it's likely to catch syntax issues you wouldn't. Record `"source": "mcp"`
   for each diagram it produced.
3. **Otherwise, generate natively.** Write Mermaid syntax directly,
   following `references/mermaid-syntax-guide.md` for the diagram types
   most likely to be needed (component/flowchart, sequence, ER, state).
   Record `"source": "native"`.
4. **Validate where possible.** If a Mermaid CLI or linter is available in
   the environment (e.g., `mmdc` via npx, or a local mermaid-cli install),
   run it against each diagram file and fix reported syntax errors before
   finalizing: `npx -y @mermaid-js/mermaid-cli --version` is a reasonable
   probe (only run this if you have network/npm access; if you don't, skip
   straight to manual review). Record `"validated": true` only for diagrams
   an actual tool checked — a diagram you only read over yourself is
   `"validated": false`, however confident it looks.
5. **Report limitations.** List anything not tool-validated, or any
   section too ambiguous to render faithfully, in `limitations`.

Do this for every diagram you decided the content warrants — don't add
diagrams the content doesn't support.

## Output structure

Each version is a **directory**, not a single file:

```
<project-root>/mermaid-diagrams/v<version>/
  01-<kebab-case-name>.mmd
  02-<kebab-case-name>.mmd
  index.md
```

`<project-root>` is the `path` from Step 1's `resolve-project` output.

Number files in the order listed under "Deriving diagrams from content"
above (system context, then component architecture, then request flows,
then data model, then deployment, then event flow, then failure/recovery
— skipping whichever weren't warranted). `index.md` follows
`templates/mermaid-diagrams.md` — a short human-readable index of what's
in the directory (name, type, what it shows, source, validated). See
`examples/url-shortener-mermaid.md` for a fully worked directory plus its
matching `data.json`.

Alongside the directory, produce a `.data.json` following
`schema/mermaid-diagrams.schema.json` — `project-readme` reads this
directly afterward to know what diagrams to embed, so its `index.md`-like
completeness matters even though this isn't a hard-gated dependency for
you the way FR/NFR are for architecture-design.

## No hallucination

If the architecture document describes a component relationship
ambiguously (e.g., it's unclear whether two services communicate
synchronously or via an event), don't pick one to make the diagram look
complete — render what's unambiguous and list the ambiguity in
`limitations`, tied back to the relevant architecture section.

## Human review checkpoint — before writing anything to disk

Render each diagram **directly in your response** (as Mermaid code blocks),
not to disk yet. Then ask something like: *"Here are the diagrams
generated from the architecture design. Do these look right, or is there
anything you'd like adjusted before I lock this in as v\<version\>?"* Stop
and wait for their reply in a new turn.

If they ask for changes, revise and ask again — remember this is
extraction, not redesign, so a requested change that would alter the
architecture itself (not just how it's drawn) should be redirected back to
`architecture-design` rather than made here. Repeat until the user
explicitly confirms, or explicitly tells you to proceed without further
review. This applies even when the orchestrator invoked you.

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version mermaid-diagrams`
2. Write `<project-root>/mermaid-diagrams/v<version>/` (the `.mmd` files +
   `index.md`) and `<project-root>/mermaid-diagrams/v<version>.data.json`.
3. Record `inputs_consumed` for `architecture-design` (version + hash from
   the `check-ready` output above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data mermaid-diagrams --path <project-root>/mermaid-diagrams/v<version>.data.json`
5. Write the envelope to `<project-root>/mermaid-diagrams/v<version>.envelope.json`,
   with `"document_path"` set to the **directory** (not a file inside it),
   `status` set to `READY` or `BLOCKED_QUESTION` per
   `references/pipeline-conventions.md`'s mapping table, and
   `"next_skill": "project-readme"`.
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/mermaid-diagrams/v<version>.envelope.json`
   (it hashes the whole directory automatically).
7. Report to the user the version produced, which diagrams were generated,
   which method (MCP vs native) and validation level each used, and that
   `project-readme` can now run.
