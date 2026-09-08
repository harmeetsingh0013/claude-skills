---
name: mermaid-js
description: Extracts Mermaid.js diagram files from a Final Architecture Design Document's diagram specifications, as stage 4 (final stage) of a four-stage design pipeline (functional-requirements → non-functional-requirements → architecture-design → mermaid-js). Use this when the user wants diagrams (component, sequence, ER, state, flowchart, etc.) generated from an already-completed architecture design, or explicitly asks to run/update the "mermaid" / "diagrams" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. This skill only visualizes an existing, already-decided design — it never makes or reconsiders architecture decisions; if the architecture document's diagram specification is missing or ambiguous, that's a gap to flag, not a decision to make here.
---

# Mermaid.js Diagram Generation

Your job is **extraction, not redesign**. The architecture is already
decided; you translate it into pictures. If you find yourself thinking "I
think a queue would be better here," stop — that thought belongs to
architecture-design, three stages ago, not to you. Every diagram you
produce should be traceable to something the architecture document's
Section 34 (Mermaid Diagram Specification) actually asked for. Read
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
subcommand, and its `path` (documents live in a dedicated folder under
the user's home directory, or `C:\` on Windows — see
`references/pipeline-conventions.md` — not wherever this session happens
to be running).

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

Read the `diagram_specifications` array from the `.data.json` — that's
your actual worklist, one diagram per entry, each with a `name`, `type`,
and `shows`. Cross-check it against the `.md`'s Section 34 for any
narrative detail the structured entry doesn't fully capture. If a
specification's `shows` is too vague to render faithfully, don't guess at
structure — note it as a limitation instead (see Finishing).

## Baseline for incremental updates

Run `python scripts/pipeline_tool.py --project <id> next-version mermaid-diagrams`.
If a previous version exists, read its directory — keep diagrams
unaffected by the change as-is (same filename, same content), and only
regenerate the ones whose underlying architecture specification actually
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
   specification too ambiguous to render faithfully, in `limitations`.

Do this for every entry in `diagram_specifications` — don't stop at the
first one if several were requested, and don't add diagrams the
specification didn't ask for.

## Output structure

Each version is a **directory**, not a single file:

```
<project-root>/mermaid-diagrams/v<version>/
  01-<kebab-case-name>.mmd
  02-<kebab-case-name>.mmd
  index.md
```

`<project-root>` is the `path` from Step 1's `resolve-project` output.

Number files in the order the architecture document's diagram
specification lists them. `index.md` follows `templates/mermaid-diagrams.md`
— a short human-readable index of what's in the directory (name, type,
what it shows, source, validated). See `examples/url-shortener-mermaid.md`
for a fully worked directory plus its matching `data.json`.

Alongside the directory, produce a `.data.json` following
`schema/mermaid-diagrams.schema.json` — this is the pipeline's final
artifact, so there's no further downstream skill to hand it to, but it's
still the record of what was produced and how it was validated.

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
review. This applies even when the orchestrator invoked you. Since this is
the pipeline's last stage, confirming here is the final sign-off on the
whole design, not just a handoff to another stage.

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
   `"next_skill": null` — this is the last stage.
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/mermaid-diagrams/v<version>.envelope.json`
   (it hashes the whole directory automatically).
7. Report to the user the version produced, which diagrams were generated,
   and which method (MCP vs native) and validation level each used.
