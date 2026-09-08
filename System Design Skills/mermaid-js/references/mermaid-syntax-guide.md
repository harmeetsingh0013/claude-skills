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
