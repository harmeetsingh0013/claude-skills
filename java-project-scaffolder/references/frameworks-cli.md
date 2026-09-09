# CLI frameworks: Spring Shell, picocli, or no framework

Offer these three when the user picks "CLI" in Step 2. Same discipline as the
web frameworks: look up current stable versions and Java baselines rather
than assuming, and only present an option whose current stable release
supports the selected JDK LTS.

- **Spring Shell** — best when the CLI is really an interactive shell
  (multiple commands in one running session, tab completion, command
  history) or when the project will grow alongside other Spring
  infrastructure. It sits on top of Spring Boot, so it inherits Spring Boot's
  BOM once you pull in `spring-shell-dependencies`/the Spring Boot BOM —
  don't version Spring Shell's transitive Spring dependencies independently.
  Check Spring Shell's own compatibility table (it publishes which Spring
  Boot line each Spring Shell release targets) before pairing a Spring Shell
  version with a Spring Boot version — pick the pairing from that table, not
  by combining the newest of each independently.
- **picocli** — best for a straightforward "run one command, get one
  result, exit" CLI, or when the user wants a small dependency footprint and
  first-class GraalVM native-image support (picocli has explicit, well
  documented native-image support, including an annotation processor that
  generates the reflection configuration for you — use that rather than
  hand-writing a `reflect-config.json`). It's a single small dependency with
  no framework-level BOM; check its latest stable release directly on Maven
  Central and confirm its docs don't flag any Java-version caveat.
- **No framework** — plain `Main` with `args[]` parsing by hand (or
  `java.util.Optional`/simple switch-based parsing). Appropriate when the
  user explicitly wants zero dependencies for the command-line layer, or the
  CLI genuinely has a single trivial command. Still apply the same package
  structure and code-quality tooling as the framework-based options — "no
  framework" only means no CLI-parsing library, not a different architecture.

If the user doesn't have a strong preference, ask one clarifying question:
"Will this run as one-shot commands, or as an interactive multi-command
shell?" — one-shot points to picocli or no framework; interactive shell
points to Spring Shell.
