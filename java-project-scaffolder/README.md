# java-project-scaffolder — a Claude Agent Skill

This is an **Agent Skill**: a folder containing a `SKILL.md` (instructions +
metadata) plus reference docs and a helper script. It teaches Claude how to
scaffold a production-shaped Java backend project — CLI or web, your choice
of framework, correct-for-today dependency versions, security, logging, code
quality tooling, tests, and CI — through a short guided conversation instead
of a fixed template.

It does **not** hardcode framework or dependency versions. Every time it
runs, it looks up what's actually current and compatible, because by the
time you use this, Spring Boot/Quarkus/Micronaut/Helidon and the Java LTS
lineup will have moved on from whatever was current when this skill was
written.

## What you get

- A Gradle (Kotlin DSL) project, with the Gradle wrapper committed, targeting
  a Java LTS version ≥ 21 that you choose.
- A web app (Spring Boot, Quarkus, Micronaut, or Helidon) or a CLI app
  (Spring Shell, picocli, or none) — your choice.
- A Hexagonal/Clean package layout under `in.harmeetsingh.<yourproject>`,
  with a minimal in-memory example wired end-to-end through it (REST
  endpoint or CLI command, your pick) — one entity, a create/record
  operation, and a retrieve operation, all derived from *your* project's
  domain (inferred from its name/description, or from your answer if the
  skill asks, rather than a generic placeholder).
- A JWT-based security layer on the web API — or username/password
  authentication (hashed credential storage, login-gated commands) for a
  CLI or any other non-web application.
- Logback-backed logging — done natively where the framework supports it,
  bridged (with the trade-off explained) where it doesn't.
- JUnit 5, Mockito, PMD, Checkstyle (Google Java style), and SpotBugs, wired
  into `./gradlew check`, plus optional Playwright end-to-end tests covering
  whatever scenario(s) you describe if you opt in — none are assumed.
- Your choice of executable JAR, Docker image, and/or GraalVM native image,
  depending on what the chosen framework actually supports well.
- `README.md` + `RUNBOOK.md` for the generated project, and a GitHub Actions
  workflow that builds, tests, lints, and (if selected) builds the
  Docker/native artifact.

## Installing in Claude

**Claude Code** (project-level, shareable via version control):

```bash
mkdir -p .claude/skills
cp -r java-project-scaffolder .claude/skills/
```

**Claude Code** (user-level, available in every project):

```bash
mkdir -p ~/.claude/skills
cp -r java-project-scaffolder ~/.claude/skills/
```

**Claude.ai / Cowork**: use the **Save skill** option on the packaged
`java-project-scaffolder.skill.zip` file — clicking it installs the skill
into your profile so it's available in future conversations.

Start a new conversation (or restart Claude Code) so the skill is picked up.

## Using it

Once installed, just describe what you want in plain language — you don't
need to invoke it by name:

> "Set up a new Java web project called `order-tracker` — a small service
> for the fulfillment team to track order status. I want Java 21 and Spring
> Boot."

> "I need a CLI tool, `log-triage`, that will eventually parse log files. No
> framework needed, keep it lightweight. Use whatever the latest Java LTS
> is."

From those descriptions the skill infers a domain on its own — `Order` for
the first, `LogEntry` for the second — and builds the one create/retrieve
example around it, no to-do list involved. If the name/description doesn't
point to a clear domain (e.g. `platform-poc`, "internal proof of concept"),
the skill will ask what single operation to demonstrate instead of guessing.

The skill will then walk the conversation through: project name/description
confirmation → JDK LTS choice → app type → framework → domain inference (or a
quick question if it's unclear) → (silently) version discovery and BOM
resolution → local environment check → project generation → a final summary
of exactly what versions it resolved to, what the example domain/operations
are, and where the test/quality reports live.

**Nothing is generated without a project name and a one-line description.**
If you don't provide both and there's no way to infer them from context, the
skill will ask instead of guessing — this is intentional, not a bug.

## Repository layout

```
java-project-scaffolder/
├── SKILL.md                                # Entry point: workflow + principles
├── references/
│   ├── discovery-and-versioning.md         # The discover/filter/select/verify process + BOM rule
│   ├── frameworks-web.md                   # Spring Boot / Quarkus / Micronaut / Helidon
│   ├── frameworks-cli.md                   # Spring Shell / picocli / none
│   ├── architecture-and-example.md         # Hexagonal layout + deriving the example from the project's domain
│   ├── security-jwt.md                     # JWT per framework, plus the CLI equivalent
│   ├── logging-logback.md                  # Logback native vs. bridged, per framework
│   ├── code-quality.md                     # JUnit, Mockito, PMD, Checkstyle, SpotBugs, Playwright
│   ├── build-types.md                      # Executable JAR / Docker / native, per framework
│   └── ci-cd-github-actions.md             # GitHub Actions workflow template
└── scripts/
    └── verify_environment.sh               # Checks local JDK major version + Gradle presence
```

## Why it's built this way

The instructions deliberately avoid `if Java 21 → X, if Java 25 → Y`-style
branching and avoid pinning specific framework/library versions in the skill
itself. Both go stale the moment a new release ships. Instead, the skill
encodes a *process* — discover what's current, filter for compatibility,
select the best fit, generate against it, and verify the result actually
builds — so it keeps producing a correct, current project long after any
version numbers written here would have gone out of date.
