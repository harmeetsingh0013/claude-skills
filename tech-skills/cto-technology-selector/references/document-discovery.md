# Document discovery

Read this when the user has supplied (or referenced) design documents of any kind — a path, uploaded files, or pasted content.

## What counts as a design document

mini-PRD · functional requirements · non-functional requirements · architecture design · Mermaid diagrams · sprint plans · ADRs · existing architecture documentation · deployment documentation · API specifications · database/data-model documentation · security requirements · infrastructure documentation · existing source code (when available).

A project might be laid out like:

```
project/
├── mini-prd/
├── functional-requirements/
├── non-functional-requirements/
├── architecture-design/
├── mermaid-js/
└── sprint-planning/
```

Don't assume this exact structure exists — it's one common shape, not a requirement. Look at what's actually there.

## The inspection sequence

1. Inspect the path/files.
2. Identify which documents are actually relevant.
3. Determine which are authoritative (a stale draft and a signed-off architecture doc don't carry equal weight).
4. Check for schemas/templates the documents were written against, if useful for understanding intent.
5. Cross-check documents against each other.
6. Identify contradictions between them.
7. Identify what's missing.
8. Build an internal model of the system from all of this.
9. Only then start technology selection.

**Don't blindly trust filenames.** A file called `architecture.md` does not automatically constitute a valid architecture specification — open it and judge the content. If it's thin or aspirational rather than decided, treat it as a weak signal, not ground truth, and say so.

## If the documents came from a staged pipeline

Some projects use a staged document-generation pipeline where each stage has its own schema/templates/examples, something like:

```
mini-prd/                    (stage 0)
functional-requirements/     (stage 1)
non-functional-requirements/ (stage 2)
architecture-design/         (stage 3 — usually the richest source)
mermaid-js/                  (stage 4)
sprint-planning/             (on request)
```

Each stage folder typically has its own `templates/`, `examples/`, and `references/` — useful for understanding what the document *should* contain and whether what you're looking at is complete or partial. If you find yourself inside such a pipeline, the `architecture-design` stage is usually your richest source for technology-relevant constraints (it's typically the largest and most decision-dense of the set), but don't skip the earlier stages — functional and non-functional requirements are where the actual constraints originate, and architecture documents sometimes encode decisions without restating the requirement that drove them.

## Output of this step

You should be able to state, in your own words, what the system does, who it serves, what it must guarantee (performance, availability, consistency, security), what already exists that must be respected, and what's still undecided or contradictory — before opening any conversation about specific technologies. If you can't state these yet, you're not done reading.
