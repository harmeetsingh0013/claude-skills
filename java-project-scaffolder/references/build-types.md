# Build types: executable, Docker, native

Always offer an **executable JAR** — every framework here supports it, so it
should be the guaranteed baseline. Offer **Docker** and **GraalVM native
image** only where the selected framework's own tooling genuinely supports
them well; don't offer an option just because the user's original request
mentioned it in the abstract if the specific framework choice makes it
painful or unsupported.

- **Spring Boot** — executable JAR via the `org.springframework.boot` Gradle
  plugin's `bootJar` task (already the default packaging). Docker via
  Spring Boot's built-in Cloud Native Buildpacks support (`bootBuildImage`
  task) — no separate Dockerfile needed unless the user wants one. GraalVM
  native image via the `org.graalvm.buildtools.native` Gradle plugin plus
  `spring-boot-starter` reflection hints where needed — check the current
  Spring Boot version's native-image documentation for any framework
  features that aren't yet native-image-friendly before promising full
  support.
- **Quarkus** — executable JAR via its default `quarkus-gradle-plugin`
  `quarkusBuild` task (fast-jar by default). Docker via Quarkus's generated
  `Dockerfile.jvm`/`Dockerfile.native` under `src/main/docker/` plus its
  container-image extensions (`quarkus-container-image-docker` or
  `-jib`). Native image is a first-class, well-documented Quarkus feature —
  `quarkusBuild --native` (requires a local GraalVM/Mandrel or
  container-based build).
- **Micronaut** — executable JAR via the `io.micronaut.application` Gradle
  plugin. Docker via the same plugin's `dockerBuild`/`dockerBuildNative`
  tasks. Native image is also first-class here via
  `io.micronaut.application`'s GraalVM integration.
- **Helidon** — executable JAR is the default build output. Docker via the
  `Dockerfile` templates Helidon's project generator provides (or hand-roll
  a simple multi-stage one from an OpenJDK base image). Native image is
  supported for Helidon SE and MP but with more manual GraalVM configuration
  than Quarkus/Micronaut — check Helidon's current native-image guide before
  offering it as equally turnkey.
- **CLI — Spring Shell** — executable JAR is straightforward (it's a Spring
  Boot app under the hood). Native image inherits Spring Boot's native-image
  constraints above; interactive shells add extra reflection-configuration
  surface, so verify against Spring Shell's own native-image notes if the
  user picks it. Docker makes sense only if the CLI is meant to run inside a
  container (e.g. as a Kubernetes Job) — ask before assuming that's wanted
  for a CLI.
- **CLI — picocli** — executable JAR (a fat/shadow JAR via the
  `com.github.johnrengelman.shadow`/Gradle's built-in shadow successor, or
  simply a runnable JAR with a `Main-Class` manifest and `Class-Path`).
  picocli has first-class, well-documented GraalVM native-image support via
  its annotation processor (`picocli-codegen`), which is one of picocli's
  strongest selling points — offer it readily. Docker only if the CLI is
  meant to run containerized.
- **CLI — no framework** — executable JAR only, unless the user specifically
  wants native image, in which case GraalVM's native-image tool still works
  on plain Java with manual reflection configuration (there's no
  annotation-processor convenience without picocli) — set expectations
  accordingly.

Whatever is chosen, verify it by actually running the corresponding Gradle
task once (Step 15) rather than only generating the configuration — a native
image or Docker build step that's never been executed is the most likely
place for a subtly wrong version pin to surface.
