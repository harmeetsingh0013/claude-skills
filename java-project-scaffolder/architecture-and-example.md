# Architecture and the example feature

## Package layout

Root every package at `in.harmeetsingh.<projectname>` (projectname in
lowercase, no hyphens — collapse or camelCase them for the Java package
segment while keeping the hyphenated form for the Gradle/repo name). Use
Hexagonal (Ports & Adapters) framing, since it maps cleanly onto both a web
app and a CLI app without forcing web-specific naming ("controller") into a
CLI project:

```
in.harmeetsingh.<projectname>
├── domain
│   ├── model          # Plain Java records/classes for the inferred domain entity
│   └── port
│       ├── in         # Use-case interfaces driven BY the outside world
│       └── out        # Interfaces the domain needs FROM the outside world (a repository port)
├── application
│   └── service        # Use-case implementation(s)
└── adapter
    ├── in
    │   ├── web         # REST controllers/resources (web apps) — depend on domain.port.in only
    │   └── cli          # Commands (CLI apps) — depend on domain.port.in only
    └── out
        └── memory       # In-memory repository implementation (ConcurrentHashMap/List) — implements domain.port.out
```

Only generate the `web` or `cli` adapter subpackage that matches the chosen
app type — don't scaffold the unused one. The security adapter (Step 8)
lives under `adapter.in.web.security` for web apps.

## Deriving the example feature from the project's domain — do this, don't default to a to-do list

**Never generate a to-do-list example by default.** The to-do list was only
ever a placeholder used to illustrate this skill; it does not belong in a
real generated project. Every generated project's example must come from the
actual domain the user is building, determined like this, in order:

1. **Infer from the project name and description gathered in Step 0.** Most
   names/descriptions state or clearly imply a domain — "order-tracker" /
   "tracks order status for the fulfillment team" implies an `Order` entity
   with something like "record a new order" and "look up an order's status."
   "invoice-service" implies an `Invoice`. "log-triage" implies a `LogEntry`
   or similar. Read the name and description literally; do not invent a
   domain that isn't supported by what the user actually said, and do not
   default to a generic placeholder (to-do, "widget", "item", "thing") when
   a real domain is inferable.
2. **If the name/description is genuinely ambiguous or too generic to name a
   domain entity with any confidence** (e.g. the project is named after a
   team, an internal codename, or something purely technical like
   "api-gateway-poc" with a description that doesn't describe a business
   domain) — **stop and ask the user directly** what example they'd like the
   scaffold to implement, rather than guessing. A short, concrete question
   works best: "What's one simple operation this project should demonstrate
   — e.g. for an X, that might be 'register an X' and 'look up an X'. What
   would make sense here?" Don't proceed past this point until you have an
   answer.
3. **Do not ask when the domain is clearly inferable.** Asking anyway when
   the answer is obvious from the name/description is friction, not safety —
   reserve the question for genuine ambiguity.

Whatever domain is settled on (inferred or user-specified), keep the example
to exactly **one entity and two operations**: something that *creates/records*
an instance, and something that *retrieves* it (single lookup or list —
whichever the domain suggests reads more naturally). Do not build out more of
the domain than that — no update, no delete, no relations to other entities,
no persistence beyond memory. The point is to prove the architecture and
wiring compile and run end-to-end, not to build a real feature.

- **Entity**: a single Java record capturing the minimal fields implied by
  the domain and description (an id plus one or two descriptive fields is
  usually enough — don't invent fields the user never mentioned).
- **Storage**: a single `ConcurrentHashMap<String, TheEntity>` (or
  `CopyOnWriteArrayList<TheEntity>` if the domain is naturally list-like and
  keyed lookup doesn't make sense) behind the repository port. No database,
  no file persistence.
- **Web app**: expose two REST endpoints (a `POST` to create/record, a `GET`
  to retrieve) named after the actual domain noun — not `/api/todos` — on
  whichever web layer the selected framework provides (Spring MVC
  `@RestController`, JAX-RS/Quarkus `@Path`, Micronaut `@Controller`, or
  Helidon's routing). Protect the creating endpoint with the JWT layer from
  `security-jwt.md`; the retrieval endpoint can be left open or also
  protected — pick one and say which, don't leave it ambiguous.
- **CLI app**: expose two commands named after the actual domain operations
  (e.g. `record` / `find`, or whatever verbs fit the inferred domain best),
  using whichever command style the selected framework provides (Spring
  Shell `@ShellMethod`, picocli `@Command`/`@Parameters`, or a hand-rolled
  `switch` on `args[0]` for "no framework"). Gate the creating command behind
  the username/password login described in `security-jwt.md`.

State in the generated README, in one or two lines, what domain was inferred
(or supplied by the user) and what the two example operations are, so the
choice is transparent rather than a silent guess.

## Tests for the example (see also `code-quality.md`)

- **Unit test**: test the application service directly against a
  fake/in-memory repository implementation (or the real in-memory adapter,
  since it has no external dependency anyway) — no framework context needed.
  Always generate this, regardless of domain.
- **Integration test**: for web apps, boot the framework's test slice (e.g.
  Spring Boot's `@SpringBootTest`/`MockMvc` or `WebTestClient`, Quarkus's
  `@QuarkusTest`, Micronaut's `@MicronautTest`, Helidon's test support) and
  hit the real HTTP endpoints, including a case that exercises the JWT
  protection (rejected without a token, accepted with a valid one). For CLI
  apps, invoke the actual command entry point (Spring Shell's test support,
  picocli's `CommandLine` programmatically) and assert on output/exit code,
  including a case that exercises the username/password gate. Always
  generate this, regardless of domain.
- **End-to-end test**: unlike unit and integration tests, **do not generate
  this by default**. Its scope depends entirely on what the user asks for
  when Step 11 poses the question — if they decline, generate none; if they
  accept, build the E2E test(s) around exactly the scenario(s) they describe
  (see `code-quality.md` for the Playwright wiring). Don't invent an E2E
  scenario the user didn't ask for.
