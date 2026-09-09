# Discovery and versioning

This is the core anti-hallucination workflow for the skill. Follow it exactly
for whichever framework was selected in Step 3. Do not fill in version
numbers from memory or training data — frameworks release every few weeks,
and a plausible-looking version string that isn't actually the current stable
release will produce a project that doesn't resolve.

## The five-stage process

1. **Discover** — Find the current stable release line of the selected
   framework and, where relevant, its Java baseline. Use the framework's own
   source of truth, in this order of preference:
   - The framework's official releases/versions page (e.g. Spring Boot's
     GitHub releases, Quarkus's `quarkus.io` release notes, Micronaut's
     `micronaut.io` docs, Helidon's GitHub releases).
   - Maven Central / the Gradle plugin portal for the exact latest
     non-milestone, non-RC, non-SNAPSHOT version string.
   - The framework's own compatibility matrix or system requirements page for
     its minimum/target JDK.
2. **Filter** — Discard anything that is: a milestone (`M1`), release
   candidate (`RC1`), snapshot, or explicitly marked unsupported/EOL for the
   line you're considering. Discard any release whose documented minimum
   Java version is higher than what's achievable, or whose support window
   doesn't cover the JDK LTS chosen in Step 1 (some frameworks lag a new JDK
   LTS by weeks to months — if the just-released JDK LTS isn't yet supported
   by any stable release of the desired framework, say so and ask whether the
   user wants to fall back to the previous JDK LTS instead of silently doing
   it for them).
3. **Select** — Choose the newest release that survives the filter. Prefer
   the newest **minor** line with an active support policy over the newest
   patch of an older line, unless the user asked for maximum stability, in
   which case prefer the most recent line that's been out long enough to have
   at least one or two patch releases.
4. **Generate** — Write the build file against that exact version, and pull
   in the framework's BOM/platform (Spring Boot's `io.spring.dependency-management`
   plugin or its BOM import, Quarkus's `quarkus-bom`, Micronaut's
   `micronaut-bom`/`micronaut-platform`, Helidon's `helidon-bom`) so that every
   dependency the BOM manages inherits its version from the BOM, not from you.
   For any dependency the BOM does *not* manage (a JWT library, Checkstyle,
   PMD, SpotBugs, Playwright — see `code-quality.md` and `security-jwt.md`),
   independently discover its latest stable release and confirm — from its own
   docs/release notes — that it supports the selected JDK.
5. **Verify** — After generating the build file, actually resolve
   dependencies (`./gradlew dependencies` or an equivalent resolution-only
   task) and compile (`./gradlew compileJava compileTestJava`) before moving
   on. A version that looked right on paper can still fail to resolve (wrong
   artifact coordinates, a yanked release) or fail to compile against the
   chosen JDK (an API removed or a new compiler restriction). Catch that here,
   not after handing the project to the user.

## Why "don't independently version" matters

Concretely: if Spring Boot's BOM pins Jackson to `2.18.x`, do not write
`com.fasterxml.jackson.core:jackson-databind:2.19.0` into the build file just
because 2.19.0 exists on Maven Central. Spring Boot's own integration tests
were run against 2.18.x; jumping Jackson ahead of the BOM can silently change
serialization edge cases (date/time handling, module auto-registration
behavior) that the framework doesn't expect. The same logic applies to
Tomcat/Netty/Undertow, SLF4J, JUnit's platform version supplied by a
framework's test starter, etc. When you want a newer version of something the
BOM manages, the correct move is to upgrade the *framework*, not the
individual artifact — and if the user specifically wants a dependency newer
than what the current stable framework BOM offers, tell them that's an
explicit override with a compatibility risk, rather than doing it silently.

## Recording what you resolved

When you report back to the user (Step 15 of SKILL.md), state the resolved
framework version and the 2-4 headline dependency versions its BOM pulled in
(e.g. "Spring Boot 3.4.1 → Spring Framework 6.2.1, Jackson 2.18.2, embedded
Tomcat 10.1.34, JUnit Jupiter 5.11.4"). This makes the BOM-driven selection
auditable instead of a black box.
