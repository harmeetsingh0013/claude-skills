# Mermaid syntax quick reference (native-generation fallback)

Use this when no MCP Mermaid tool is available. Keep syntax simple and
widely compatible rather than using newer/less common features that some
renderers don't support.

## Component / flowchart

```mermaid
flowchart TD
    Client[Client] -->|HTTPS| API[API Service]
    API --> DB[(Postgres)]
    API --> Cache[(Redis)]
    API -->|publish| Queue[[Event Queue]]
    Queue --> Worker[Analytics Worker]
```

- `-->` solid arrow, `-.->` dashed, `-->|label|` for a labeled edge
- `[(...)]` for databases/stores, `[[...]]` for queues, `[...]` for generic
  nodes, `{...}` for decisions

## Sequence diagram

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as Database
    U->>A: POST /links
    A->>D: INSERT link
    D-->>A: OK
    A-->>U: 201 Created
```

- `->>` solid call, `-->>` dashed return
- `activate`/`deactivate` to show lifelines if the sequence has concurrent
  actors worth highlighting

## Entity-relationship diagram

```mermaid
erDiagram
    TEAM ||--o{ MEMBER : has
    MEMBER ||--o{ LINK : creates
    LINK ||--o{ CLICK_EVENT : generates
```

- `||--o{` one-to-many, `||--||` one-to-one, `}o--o{` many-to-many

## State diagram

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Processing: upload received
    Processing --> Ready: processing succeeded
    Processing --> Failed: processing error
    Ready --> [*]
    Failed --> [*]
```

## Context map (approximated as a labeled flowchart)

Mermaid has no dedicated diagram type for DDD context maps — render it as
a flowchart with each bounded context as a node and each relationship as
a labeled edge carrying the pattern name from architecture-design's
Context Map section (Partnership, Shared Kernel, Customer-Supplier,
Conformist, Anticorruption Layer, Open Host Service, Published Language,
Separate Ways):

```mermaid
flowchart LR
    BC01["BC-01: Link Management"]
    BC02["BC-02: Analytics"]
    BC03["BC-03: Team & Access"]
    BC03 -->|Customer-Supplier| BC01
    BC01 -->|"Published Language (LinkClicked)"| BC02
```

Keep edge labels short — the pattern name plus, in parentheses, the
concrete mechanism (a domain event name, a shared table, etc.) if there's
room. Don't try to show aggregates or tactical detail on this diagram;
that's what an entity-relationship diagram is for.
