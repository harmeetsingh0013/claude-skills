<!--
This is the template for design-docs/mermaid-diagrams/v<version>/index.md —
a human-readable index that lives INSIDE the version directory alongside
the .mmd files (01-system-context.mmd, etc.). The directory as a whole is
this stage's "document_path"; this index.md is not itself the document_path
and is not separately versioned outside the directory.
-->

# Mermaid Diagram Artifacts

Generated from: architecture-design v<version>

## Diagrams

### 01-system-context.mmd
**Type:** system-context
**Shows:** <restate what the architecture spec asked for>
**Source:** mcp | native
**Validated:** yes (via <tool>) | manual review only

### 02-container-architecture.mmd
...

(one entry per file actually produced — filenames are
`NN-kebab-case-name.mmd`, numbered in the order they appear in the
architecture document's Mermaid Diagram Specification section; only
produce the ones that section actually calls for)

## Limitations

Anything not validated by a tool, or any diagram specification from the
architecture document that was too ambiguous to render faithfully (listed
here as an open question rather than guessed at).
