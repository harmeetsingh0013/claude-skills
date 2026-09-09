# Worked example: Mermaid Diagram Artifacts — TeamLink (continued)

Derived from architecture-design v1.0's Mermaid Diagram Specification,
which asked for exactly three diagrams (not all nine types — only the
ones this particular design actually warrants).

## Output layout

```
<project-root>/mermaid-diagrams/
  v1.0/
    01-context-map.mmd
    02-request-flow.mmd
    03-entity-relationship.mmd
    index.md
  v1.0.data.json
  v1.0.envelope.json
  LATEST.json
```

`document_path` in the envelope is the directory `<project-root>/mermaid-diagrams/v1.0/`,
not a single file — this is the one stage where that's true.

## 01-context-map.mmd

Mermaid has no dedicated "context map" diagram type, so this is
approximated as a flowchart, with edge labels carrying the DDD
relationship pattern — see `references/mermaid-syntax-guide.md`.

```mermaid
flowchart LR
    BC03["BC-03: Team & Access"]
    BC01["BC-01: Link Management"]
    BC02["BC-02: Analytics"]
    BC03 -->|Customer-Supplier| BC01
    BC01 -->|"Published Language (LinkClicked)"| BC02
```

## 02-request-flow.mmd

```mermaid
sequenceDiagram
    participant V as Link Visitor
    participant A as API
    participant D as Database
    participant Q as Event Queue
    V->>A: GET /r/{code}
    A->>D: Lookup code
    D-->>A: Original URL
    A-->>V: 302 Redirect
    A->>Q: Publish LinkClicked (async)
```

## 03-entity-relationship.mmd

```mermaid
erDiagram
    TEAM ||--o{ MEMBER : has
    MEMBER ||--o{ LINK : creates
    LINK ||--o{ CLICK_EVENT : generates
```

## v1.0.data.json

```json
{
  "document_id": "MERMAID-TEAMLINK-001",
  "product": "TeamLink URL Shortener",
  "version": "1.0",
  "created": "2026-01-17",
  "input_document": {"type": "architecture-design", "version": "1.0", "validation": "PASS"},
  "status": "READY",
  "mvp": {"number": 1, "is_final": false},
  "diagrams": [
    {
      "filename": "01-context-map.mmd",
      "type": "context-map",
      "shows": "The three bounded contexts and their relationships, per architecture-design section 6.",
      "source": "native",
      "validated": false
    },
    {
      "filename": "02-request-flow.mmd",
      "type": "sequence-diagram",
      "shows": "The redirect path from visitor click through async click-event publication, per architecture-design section 10.",
      "source": "native",
      "validated": false
    },
    {
      "filename": "03-entity-relationship.mmd",
      "type": "entity-relationship",
      "shows": "Team/Member/Link/ClickEvent relationships from the data model in section 13.",
      "source": "native",
      "validated": false
    }
  ],
  "limitations": [
    "No Mermaid MCP tool or local mmdc install was available in this session; all three diagrams were generated natively and only manually reviewed for syntax, not tool-validated.",
    "Mermaid has no native context-map diagram type; 01-context-map.mmd is approximated as a labeled flowchart."
  ]
}
```

Notice `"validated": false` and the honest limitations entries — that's
the "report limitations" step of the workflow, not a failure. If an MCP
tool or `mmdc` had been available, `source` would say `"mcp"` and
`"validated"` would be `true` for whichever diagrams it actually checked.
