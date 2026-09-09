# Code quality tooling

None of these are managed by a web/CLI framework's BOM, so each needs its own
discover → filter → select → verify pass (per `discovery-and-versioning.md`),
checked specifically against the selected JDK LTS — static-analysis tools in
particular sometimes lag a brand-new JDK release (they parse bytecode/ASM
structures that change per class-file version).

- **JUnit 5 (Jupiter)** — via the `org.gradle.testing.jvm` test suite support
  or the classic `useJUnitPlatform()`. If the web framework already declares
  a JUnit BOM-managed version through its test starter (Spring Boot's
  `spring-boot-starter-test`, Quarkus's `quarkus-junit5`, Micronaut's
  `micronaut-test-junit5`), use that version rather than pinning a separate
  one — this is another instance of the BOM rule.
- **Mockito** — same logic: if the framework's test starter already brings a
  compatible Mockito in transitively, don't add a conflicting explicit
  version; only pin it directly for CLI-without-framework projects that have
  no test starter to inherit from.
- **PMD** — apply Gradle's built-in `pmd` plugin. Discover PMD's current
  stable version and confirm its release notes list support for the selected
  JDK's bytecode/language level (PMD ships its own bundled ruleset ID scheme
  per major version — verify the ruleset names you configure exist in the
  discovered version rather than assuming they're unchanged).
- **Checkstyle** — apply Gradle's built-in `checkstyle` plugin, and configure
  it with Checkstyle's bundled `google_checks.xml` (ship this via
  `toolVersion` resolution — Checkstyle bundles `google_checks.xml` inside
  its own jar, so reference it as
  `checkstyle.config = resources.text.fromArchiveEntry(checkstyleConfiguration, 'google_checks.xml')`
  or copy it into `config/checkstyle/checkstyle.xml` if the user wants it
  editable in-repo). Discover Checkstyle's current stable version compatible
  with the selected JDK before pinning `toolVersion`.
- **SpotBugs** — apply the `com.github.spotbugs` Gradle plugin. Discover its
  current stable version and confirm compatibility with the selected JDK —
  SpotBugs analyzes bytecode and has historically needed explicit updates to
  support each new class-file version.
- **JaCoCo** (not explicitly requested but implied by "code quality reports"
  in the runbook requirement) — consider offering it for coverage reporting
  alongside the others; mention it as an option rather than assuming, since
  the user didn't name it explicitly.

Wire every tool's Gradle task into `./gradlew check` so a single command
runs tests plus all static analysis, and make sure each tool's HTML/XML
report path is documented in `RUNBOOK.md`.

## Playwright E2E tests (optional, ask first)

Only add this if the user answers yes to the Step 11 question. Use
`com.microsoft.playwright:playwright` (discover its current stable version
directly — it isn't managed by any of the frameworks in this skill) as a
test-scope dependency.

- **Web app**: Playwright can drive a real browser against the running app
  for true end-to-end coverage, or use its `APIRequestContext` for pure HTTP
  E2E checks against the REST endpoints (lighter weight, often the better
  fit for a JSON API with no UI — ask the user which they mean if the app has
  no browser-rendered UI, since "E2E with Playwright" for a headless REST API
  usually means the API-request mode, not browser automation).
- **CLI app**: there's no browser surface to drive; if the user still wants
  Playwright specifically, its `APIRequestContext` only makes sense if the
  CLI talks to a remote HTTP API. For a fully local CLI (like the to-do
  example), Playwright isn't a good fit — say so, and suggest a plain
  process-invocation end-to-end test (spawn the built artifact, assert on
  stdout/exit code) instead of forcing Playwright in where it doesn't apply.

Playwright requires a one-time `playwright install` (browser binaries) step —
document that in `RUNBOOK.md` and add it to the CI workflow
(`ci-cd-github-actions.md`) if E2E tests were added.
