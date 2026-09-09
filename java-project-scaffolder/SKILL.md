---
name: java-project-scaffolder
description: Scaffolds a new production-grade Java backend project (Gradle + Kotlin DSL) from scratch — selecting a Java LTS version, a CLI or web framework (Spring Boot, Quarkus, Micronaut, Helidon, Spring Shell, picocli, or plain CLI), Clean/Hexagonal package structure, Logback logging, JWT security, JUnit/Mockito/PMD/Checkstyle/SpotBugs, and a GitHub Actions pipeline. Use this whenever the user asks to "start/bootstrap/scaffold/set up a new Java project", "create a Spring Boot / Quarkus / Micronaut / Helidon app", "set up a Java CLI with picocli / Spring Shell", or wants a Gradle project generated with a chosen JDK LTS version, even if they don't use the word "skill" or name every detail. Do NOT use this for editing an existing project's build files one-off, or for non-JVM languages.
---

# Java Project Scaffolder

## What this skill is for

This skill turns a short conversation into a compilable, tested, lint-clean Gradle
(Kotlin DSL) Java project — either a web service or a CLI tool — with a real
(if minimal) example feature **drawn from the project's own domain**, plus
security, logging, code-quality tooling, and CI already wired up. It is meant
to feel like a senior Java platform engineer ran `gradle init` and then spent
a day hardening the result.

The single most important rule governing this skill is:

> **Discover → Filter → Select → Generate → Verify.**
> Never hardcode "if Java 21 then Spring Boot 3.2" style logic. Always look up
> what is current and compatible *at the time the skill runs*, because
> frameworks, BOM versions, and even which Java versions are LTS will have
> moved on since this skill was written. Treat every version number in this
> document and its references as an *example*, never as a value to reuse.

## Non-negotiable principles

1. **Refuse without identity.** Never scaffold a project without a project
   name and a one-line description. If the user hasn't given both, don't
   invent them — either ask, or, if the conversation already contains enough
   context (a domain, a purpose, prior messages), propose 2-3 name/description
   candidates and let the user pick or edit before anything is generated.
2. **The example must come from the real domain, never a placeholder.**
   Infer the one example feature from the project's name/description. If the
   domain genuinely can't be inferred, ask the user what to build instead of
   defaulting to a generic stand-in (to-do list, "widget", etc.). See
   `references/architecture-and-example.md`.
3. **BOM-driven dependency versions, never independent ones.** Once a
   framework and its version are selected, every dependency that the
   framework's own Bill of Materials (Spring Boot's dependency-management
   plugin, Quarkus BOM, Micronaut BOM, Helidon BOM) manages must take the
   version from that BOM. Do not "upgrade" Jackson, Tomcat, Netty, SLF4J, etc.
   independently just because a newer release exists on Maven Central — that
   breaks the compatibility guarantee the BOM exists to provide. Only pick a
   dependency version yourself when the framework's BOM does not manage that
   artifact (e.g. a Checkstyle Gradle plugin, a JWT library not covered by the
   BOM) — and in that case, verify it against the selected JDK LTS version.
4. **No deprecated APIs, ever, in generated code.** Every class, test, and
   build script this skill emits must compile cleanly with
   `-Xlint:deprecation -Werror` (or the Kotlin DSL equivalent) on the selected
   JDK. If the only way to satisfy a request is through a deprecated API,
   don't silently use it — use the supported replacement, or tell the user
   the combination they asked for isn't achievable cleanly and propose the
   closest clean alternative.
5. **Verify, don't assume, local tooling.** Before generating anything, check
   that the selected JDK and a compatible Gradle are actually installed
   locally (see Step 3). If not, stop and report the gap — don't scaffold a
   project the user can't build.
6. **Explain the why, briefly, as you go.** When you pick a version or a
   library, say in one line why (e.g. "Spring Boot 3.4.x manages Jackson
   2.18.x — using that instead of the latest Jackson release keeps
   serialization behavior consistent with what Spring tested against").

## Workflow

Work through these steps in order. Each step's detail lives in a reference
file — read it when you reach that step, not all up front, to keep context
lean.

### Step 0 — Project identity

Ask for (or infer + confirm) a **project name** (kebab-case is idiomatic for
the Gradle project and repo name) and a **one-sentence description**. If the
user gave neither and the conversation gives you nothing to go on, refuse to
scaffold and ask for them directly. If the user described *what the app does*
but not a name, propose a short list of name + description pairs derived from
that description, and wait for a pick/edit before continuing.

### Step 1 — JDK LTS version

Ask the user to choose a Java LTS version, constrained to **LTS releases ≥
21**. Don't hardcode the list of LTS releases ≥ 21 — a new one may exist by
the time this skill runs. Look up the current Oracle/OpenJDK LTS schedule
(e.g. search "Java LTS releases" or check https://www.oracle.com/java/technologies/java-se-support-roadmap.html
or https://endoflife.date/java) to build the live list of options, then let
the user pick one via a simple choice.

### Step 2 — Application type

Ask: CLI or Web application?

### Step 3 — Framework selection

Offer framework choices appropriate to the app type (web: Spring Boot,
Quarkus, Micronaut, Helidon; CLI: Spring Shell, picocli, or no framework).
Read `references/frameworks-web.md` or `references/frameworks-cli.md` for how
to discover the current latest **stable** release of each candidate and its
declared minimum/target Java version, so you only ever offer frameworks that
are actually compatible with the JDK LTS chosen in Step 1.

### Step 4 — Discover and lock the compatible stack

Read `references/discovery-and-versioning.md`. This is where you resolve the
framework version, pull in its BOM, and confirm every managed dependency
(web/server stack, Jackson, logging bridge, test libraries the framework
itself ships opinions for) is compatible with the chosen JDK — without
manually re-picking versions the BOM already governs.

### Step 5 — Gradle version and wrapper

Pick the oldest Gradle line that both (a) fully supports the chosen JDK for
running the daemon (not just toolchains) and (b) is stable — check
https://docs.gradle.org/current/userguide/compatibility.html rather than
assuming. Generate the project with the Gradle wrapper (`gradlew`,
`gradlew.bat`, `gradle/wrapper/*`) pinned to that version, using the Kotlin
DSL (`build.gradle.kts`, `settings.gradle.kts`).

### Step 6 — Verify local environment

Run `scripts/verify_environment.sh <required-java-major> <required-gradle-version>`
(or reimplement the same checks inline if the shell isn't available). It
checks that a JDK of the required major version and a Gradle install are on
the `PATH`. If either check fails, **stop before generating any files** and
report exactly what's missing and how to install it — the project ships with
a Gradle wrapper for running builds, but the skill still needs a real local
JDK (and, for the very first `gradlew` invocation, a bootstrap Gradle or an
already-cached wrapper) to validate the scaffold it just created.

### Step 7 — Package structure and the example feature

Read `references/architecture-and-example.md`. Generate a Clean/Hexagonal
layout rooted at `in.harmeetsingh.<projectname>`, with a minimal in-memory
example **derived from the project's actual domain** — inferred from the
name and description gathered in Step 0. Do not default to a to-do-list
example. If the domain can't be inferred with reasonable confidence, stop
and ask the user what single operation the example should demonstrate
before generating anything — see the reference for exactly when to ask
versus when to proceed. Whatever the domain turns out to be, keep the
example to exactly one entity and two operations (create/record +
retrieve) — no more. Web apps get a REST controller/resource; CLI apps get
a command.

### Step 8 — Security layer

Read `references/security-jwt.md`. Web apps get JWT-based authentication on
the REST layer (issue + validate tokens; protect the "add" endpoint at
minimum). Any application that is **not** a web application — CLI or
otherwise — gets **username/password authentication** instead (login prompt,
hashed credential storage, gate the "add" command at minimum). Don't use JWT
outside the web case, and don't skip security for CLI apps.

### Step 9 — Logging (Logback)

Read `references/logging-logback.md` **before** wiring logging — Logback is
not every framework's native logging backend, and pretending otherwise
produces a project that silently ignores its own `logback.xml`. The reference
explains how to get genuine Logback-backed output for each framework choice,
and when to disclose a caveat to the user instead.

### Step 10 — Code quality tooling

Read `references/code-quality.md`. Wire up JUnit 5, Mockito, PMD, Checkstyle
(Google Java style), and SpotBugs, each at a version compatible with the
selected JDK LTS, as Gradle plugins with report generation enabled.

### Step 11 — Tests

Always generate a unit test and an integration test for the example feature.
Then ask whether to add end-to-end tests. Unlike the unit/integration tests,
**the end-to-end tests' scope is entirely up to the user** — don't invent
scenarios. If they say yes, ask what scenario(s) they want covered (or use
what they've already described) and build Playwright E2E tests around
exactly that; if they decline, ship with unit and integration tests only.
Read the Playwright section of `references/code-quality.md` for how to wire
`playwright-java` for a web app's HTTP endpoints (or a CLI's process
invocation) without deprecated APIs.

### Step 12 — Build type

Ask the user to choose a build/packaging type from the options valid for
their app type — see `references/build-types.md` for what's realistically
supported per framework (e.g. GraalVM native image support and its
constraints differ across Spring Boot, Quarkus, Micronaut, Helidon, and
picocli). Offer executable (fat/boot) JAR always; offer Docker and native
image only where the selected framework genuinely supports them well.

### Step 13 — README and runbook

Generate `README.md` (project name, description, quick start) and
`RUNBOOK.md` (how to build, run, test, and run each code-quality tool
individually, plus where its report lands, e.g.
`build/reports/checkstyle/main.html`).

### Step 14 — GitHub Actions CI/CD

Read `references/ci-cd-github-actions.md` and generate a workflow that builds
with the pinned JDK/Gradle wrapper, runs tests and all code-quality checks,
uploads their reports as artifacts, and — if a native or Docker build type was
chosen — builds that artifact too.

### Step 15 — Final verification

Actually run the generated build (`./gradlew build`) and the quality tools
locally before telling the user the project is ready. If anything fails,
fix the generated code/config and re-run rather than handing over a broken
scaffold. Report a short summary: JDK, Gradle, framework + version (and which
BOM-managed versions it pulled in for the headline dependencies), build
status, and test/quality report locations.

## Reference index

| File | Read it when... |
|---|---|
| `references/discovery-and-versioning.md` | Resolving the framework version and its BOM-managed dependencies (Step 4) |
| `references/frameworks-web.md` | Choosing/discovering Spring Boot, Quarkus, Micronaut, or Helidon (Step 3) |
| `references/frameworks-cli.md` | Choosing/discovering Spring Shell, picocli, or plain CLI (Step 3) |
| `references/architecture-and-example.md` | Generating the Hexagonal package layout and the to-do example (Step 7) |
| `references/security-jwt.md` | Wiring JWT for web apps / username-password for everything else (Step 8) |
| `references/logging-logback.md` | Wiring genuine Logback output per framework, with caveats (Step 9) |
| `references/code-quality.md` | JUnit, Mockito, PMD, Checkstyle, SpotBugs, and optional Playwright (Steps 10-11) |
| `references/build-types.md` | Executable JAR vs Docker vs GraalVM native, per framework (Step 12) |
| `references/ci-cd-github-actions.md` | The GitHub Actions workflow template (Step 14) |
| `scripts/verify_environment.sh` | Local JDK/Gradle presence check (Step 6) |

## When to stop and ask instead of guessing

- Project name or description missing and not inferable → ask.
- Project domain not inferable with reasonable confidence from the name and
  description → ask what single example operation to build, don't default to
  a generic placeholder.
- End-to-end test scope, when the user opts in → ask what scenario(s) to
  cover, don't invent one.
- A requested framework/Java LTS combination has no compatible stable release
  → say so plainly, don't silently substitute a different Java version.
- A requested feature would require a deprecated API → propose the clean
  alternative, explain the trade-off, don't scaffold the deprecated version.
- Local JDK or Gradle missing/mismatched → stop, report, don't scaffold.
