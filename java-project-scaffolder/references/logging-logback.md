# Logging: Logback per framework

Read this before wiring logging. Logback is **not** the native logging
backend of every framework in this skill, and generating a `logback.xml` that
the running application silently ignores is worse than not generating one —
it looks configured but isn't. Handle each framework as follows, and always
tell the user which situation applies.

- **Spring Boot** — Logback is the default logging implementation already
  wired through SLF4J. Generate `src/main/resources/logback.xml` (or
  `logback-spring.xml` to get Spring's property placeholder support) with a
  console appender and a sensible pattern. This is the straightforward case —
  no caveat needed.

- **Micronaut** — Micronaut uses SLF4J with Logback as its default binding
  out of the box (`micronaut-http-server-netty` and friends bring it in
  transitively via the Micronaut BOM). Generate
  `src/main/resources/logback.xml` the same way as Spring Boot. Confirm the
  Logback dependency is actually present after Step 4's dependency
  resolution — if the selected starter set doesn't pull it in transitively,
  add `ch.qos.logback:logback-classic` explicitly at the version the
  Micronaut BOM manages, not an independently chosen one.

- **Quarkus — needs a caveat.** Quarkus's core logging engine is JBoss Log
  Manager, not Logback; a `logback.xml` dropped into a stock Quarkus project
  is inert. To get real Logback-backed output, add the Quarkiverse
  `io.quarkiverse.logging.logback:quarkus-logging-logback` extension, which
  bridges JBoss Logging into Logback so `logback.xml` appenders actually run.
  Before using it: (1) discover its current stable version and confirm it's
  compatible with the selected Quarkus version (it's a community/Quarkiverse
  extension, not part of core Quarkus, so its release cadence and support
  lag core Quarkus — check its own compatibility notes), and (2) tell the
  user plainly that this is a bridge on top of Quarkus's own logging system,
  not a replacement for it, and that build-time log level configuration
  still goes through `application.properties`. If the user wants zero
  friction and doesn't specifically need Logback appenders (e.g. shipping
  logs to a system with an off-the-shelf Logback appender), mention that
  configuring Quarkus's native `application.properties` logging directly is
  the first-class path and ask which they'd prefer, rather than silently
  picking the bridge.

- **Helidon — needs a caveat.** Helidon defaults to `java.util.logging`
  (JUL), configured via `logging.properties`, not Logback. To get Logback
  output, route JUL through SLF4J with `jul-to-slf4j` (`org.slf4j:jul-to-slf4j`)
  installing a `SLF4JBridgeHandler`, with `ch.qos.logback:logback-classic` as
  the actual SLF4J binding, then generate `logback.xml`. This is a bridging
  approach with a small performance cost (JUL levels get translated on every
  log call) and a startup-ordering requirement (the bridge must install
  before any JUL logging happens) — call this out to the user rather than
  presenting it as Helidon's native behavior.

## What to tell the user

In the generated README/runbook, state for the chosen framework whether
Logback is native (Spring Boot, Micronaut) or bridged (Quarkus, Helidon), and
if bridged, name the bridge dependency and its one-line limitation. Don't let
"the project contains a Logback setup" quietly mean "a logback.xml file that
does nothing."
