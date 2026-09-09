# Web frameworks: Spring Boot, Quarkus, Micronaut, Helidon

Offer these four when the user picks "web" in Step 2. For each candidate,
before presenting it as an option, look up (don't assume from memory):

- Its current stable release line (see `discovery-and-versioning.md` for the
  discover/filter/select process).
- Its documented minimum and/or recommended Java version for that release
  line, from the framework's own requirements page.
- Whether that release line's support window covers the JDK LTS chosen in
  Step 1.

Only present a framework as a choice if a stable release exists whose
documented Java support includes the selected LTS. If none of the four
qualify for a very new JDK LTS (a brand-new LTS release can outpace framework
adoption by weeks or months), say so explicitly and offer the user the choice
of waiting, or dropping back to the previous JDK LTS.

## What distinguishes them (for framing the choice to the user, not for
picking a version)

- **Spring Boot** — the default choice for teams already in the Spring
  ecosystem; largest library/integration surface; auto-configuration; Logback
  is its native default logging backend, which makes Step 9 simplest here.
  Look up its current version and Java baseline from its official
  documentation/GitHub releases and its "system requirements" page.
- **Quarkus** — container/Kubernetes-native, fast startup, strong GraalVM
  native-image story, built around Jakarta/MicroProfile APIs. Its logging
  backend is JBoss Log Manager, not Logback — read `logging-logback.md`
  before promising Logback support here. Look up its current version and
  Java baseline from quarkus.io's release notes.
- **Micronaut** — compile-time dependency injection (no runtime reflection
  for DI), fast startup, also strong on GraalVM native image, uses SLF4J with
  Logback as a common default. Look up its current version and Java baseline
  from micronaut.io's documentation.
- **Helidon** — has two programming models (SE — reactive, minimal; MP —
  Jakarta/MicroProfile-based); defaults to `java.util.logging`, not Logback —
  read `logging-logback.md` before wiring logging. Look up its current
  version, which model(s) it recommends for new projects, and its Java
  baseline from helidon.io.

When presenting the choice, prefer a short one-line framing per option (what
it's good at) over reciting version numbers — the version numbers only
matter once discovery has actually happened for the selected one.
