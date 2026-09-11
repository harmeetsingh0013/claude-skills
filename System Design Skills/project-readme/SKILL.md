---
name: project-readme
description: Produces a project-root README.md — a brief overview plus links to every available document's folder (Mini-PRD, Functional Requirements, Non-Functional Requirements, Architecture & Design, Diagrams, and Sprints if any) and every Mermaid diagram embedded inline, as the sixth and final stage of the design pipeline (mini-prd → functional-requirements → non-functional-requirements → architecture-design → mermaid-js → project-readme). Use this once mermaid-js has finished, when the user wants a project overview, an index of available documents, or a README for the project folder, or explicitly asks to run/update the "project readme" stage. Also use it when re-invoked by the design-pipeline-orchestrator skill. This is not a detailed explanation of the project — it's a brief front door that links out to the real documents; don't restate functional, non-functional, or architectural detail here.
---

# Project README

You produce a short, welcoming front door for the project folder — not a
summary of everything the other documents already say in detail. Someone
landing on this file should understand what the project is in a few
sentences, see what documents exist, and be able to get to any of them
(and any of their versions) in one click. Read
`references/pipeline-conventions.md` once at the start of a session if
you haven't already.

## Step 1: Get the project ID

Before anything else, work out which project this is —
`references/pipeline-conventions.md` has the exact procedure (check
conversation for an existing ID or a path to existing documents,
otherwise ask the user whether it's new/existing/a path, then confirm via
`resolve-project`). This skill is never the first stage run for a
brand-new project, so you should normally be *confirming* an ID the user
already has. Every `pipeline_tool.py` call below assumes a confirmed
`--project <id>`, placed **before** the subcommand, and its `path`
(documents live in a dedicated folder wherever the user chose when the
project was created — see `references/pipeline-conventions.md`).

## Input gate

```
python scripts/pipeline_tool.py --project <id> check-ready mermaid-diagrams
```

If this fails, stop and report the message — don't generate a README
pointing at diagrams that don't exist yet or aren't finalized. Because
mermaid-diagrams itself requires architecture-design, which requires FR
and NFR, which requires mini-prd, a `READY` result here guarantees all of
those exist too — you don't need to separately gate on each of them.

## Discover what actually exists — don't hardcode the document list

```
python scripts/pipeline_tool.py --project <id> list-doc-types
```

This returns every document type this project actually has, with its
current version and status — including `sprints/sprint-NN` entries if any
sprints exist. Build the "Documents" table and any "Sprints" section from
this output, not from an assumed fixed list — a project that hasn't run
`sprint-planning` yet should get no Sprints row, and re-running this skill
later (after sprints exist) should pick them up automatically without any
other change to how you work.

Read the Mini-PRD's `.data.json` for the overview — its `problem_statement`
and `primary_goal` fields are exactly the 2-4 sentences this README needs.
Don't re-derive an overview from the functional requirements or
architecture document; the Mini-PRD is the source for "what is this and
why."

Read mermaid-diagrams' `index.md` and each `.mmd` file in its latest
version directory — that's your diagram list and content to embed,
in the same order the index lists them.

## Scope discipline: brief, not comprehensive

This is the easiest place to accidentally duplicate the other documents'
work. This README does not explain:
- detailed functional behavior (that's functional-requirements)
- quality attributes or SLAs (that's non-functional-requirements)
- architectural decisions or trade-offs (that's architecture-design)
- implementation tasks (that's sprint-planning)

It only says what the product is (briefly), what documents exist, and
shows the diagrams. If you find yourself writing more than a short
paragraph of prose outside the Documents and Diagrams sections, that's a
sign you're duplicating content that belongs in a linked document instead.

## Embedding diagrams

Copy each `.mmd` file's actual content into a ```mermaid fenced code
block — verbatim, not re-derived or summarized — so it renders inline
wherever this file is viewed (GitHub, GitLab, and most markdown viewers
render Mermaid fenced blocks natively). Give each one a short caption
from mermaid-diagrams' own `shows` field for that diagram, so a reader
knows what they're looking at without having to open the diagrams folder.

## Links go to folders, not to a single locked-in version

For every document, link to its **folder** (e.g. `./functional-requirements/`),
not to a specific version file. Landing in the folder is what lets someone
freely browse and pick whichever version they need (`v1.0.md`, `v1.1.md`,
...) — a link to one hardcoded version would go stale the moment that
document is revised, silently pointing at an outdated copy. Still mention
the *current* version number as plain text next to the link so a reader
knows what they'd see by default, without that number being the thing
they click.

## No hallucination

Only list a document or embed a diagram that `list-doc-types` and
mermaid-diagrams' own index actually confirm exist. Don't invent an
overview detail that isn't in the Mini-PRD, and don't describe a document
as containing something you haven't actually read.

## Human review checkpoint — before writing anything to disk

Draft the complete README **directly in your response**, not to disk yet.
Then ask something like: *"Here's the project README — does the overview
read right, and do the linked documents and diagrams look complete? I'll
place this as v\<version\> here and also copy it to \<project-root\>/README.md
so it's visible at the project root."* Stop and wait for their reply in a
new turn.

If they want changes, revise and ask again. Repeat until the user
explicitly confirms, or explicitly tells you to proceed without further
review.

## Finishing

Once the user has confirmed the draft (or told you to proceed without
further review):

1. Get your version: `python scripts/pipeline_tool.py --project <id> next-version project-readme`
2. Write `<project-root>/project-readme/v<version>.md` (from
   `templates/project-readme.md`) and
   `<project-root>/project-readme/v<version>.data.json` (per
   `schema/project-readme.schema.json`) — `<project-root>` is the `path`
   from Step 1's `resolve-project` output.
3. Record `inputs_consumed` for `mermaid-diagrams` (version + hash from
   the `check-ready` output above).
4. Validate your own data file:
   `python scripts/pipeline_tool.py --project <id> validate-data project-readme --path <project-root>/project-readme/v<version>.data.json`
5. Write the envelope to `<project-root>/project-readme/v<version>.envelope.json`,
   with `status` `READY` (or `BLOCKED` only if `list-doc-types` came back
   missing something the gate should have guaranteed — genuinely
   shouldn't happen, but don't paper over it if it does) and
   `"next_skill": null` — this is the pipeline's true final stage.
6. Run `python scripts/pipeline_tool.py --project <id> finalize <project-root>/project-readme/v<version>.envelope.json`
7. **Copy the finalized `.md` to `<project-root>/README.md`**, overwriting
   whatever's there — this is what makes it visible as an actual README
   at the project root, not just another versioned document buried in a
   subfolder (e.g. `cp <project-root>/project-readme/v<version>.md
   <project-root>/README.md` on macOS/Linux, `copy` on Windows). The
   versioned copy in `project-readme/` stays as the historical record;
   the root copy is always the current one.
8. Report to the user: the version produced, and that `README.md` is now
   available at the project root. Since this is the pipeline's last
   stage, this is also a natural point to mention `sprint-planning` if the
   design is complete and the user hasn't run it yet.

See `examples/url-shortener-project-readme.md` for a fully worked README
plus its matching `data.json`.
