# Security layer: JWT (web) / username-password (everything else)

## Web apps

Every web framework option needs a JWT layer on the REST API. The mechanics
differ, so discover the current recommended approach for the *selected*
framework rather than reusing a pattern from a different one:

- **Spring Boot** — use `spring-boot-starter-security` plus
  `spring-boot-starter-oauth2-resource-server` (its resource-server support
  covers JWT validation without you hand-rolling a filter), or
  `io.jsonwebtoken:jjwt` if the project needs to *issue* tokens itself (e.g.
  a `/login` endpoint) rather than only validate tokens issued elsewhere.
  Both are BOM-managed or independently versioned respectively — apply the
  BOM rule from `discovery-and-versioning.md`: `spring-boot-starter-*`
  versions come from the Spring Boot BOM; `jjwt`'s version is chosen and
  verified independently since Spring Boot doesn't manage it.
- **Quarkus** — use the `quarkus-smallrye-jwt` extension (issuance) and/or
  `quarkus-smallrye-jwt` for validation via MicroProfile JWT annotations
  (`@RolesAllowed`, injecting `JsonWebToken`); its version comes from the
  Quarkus BOM/platform.
- **Micronaut** — use `micronaut-security-jwt`, version from the Micronaut
  BOM; annotate endpoints with `@Secured`.
- **Helidon** — use Helidon Security's JWT provider
  (`helidon-security-providers-jwt-auth` for MP, or the SE security module's
  JWT support), version from the Helidon BOM.

Minimum viable implementation for the example app: an endpoint (or a fixed
dev credential, clearly labeled as such) that issues a signed JWT, and the
example's creating endpoint (see `architecture-and-example.md` for how that
endpoint is named and derived from the project's domain) requiring a valid
bearer token. Sign with a
symmetric key read from configuration/environment (not hardcoded in source)
for the example; note in the README that production use should rotate this
secret and consider asymmetric signing (RS256/ES256) with a proper key
management story.

## CLI apps

JWT (bearer tokens over HTTP) is a web-API concept and doesn't apply to a
local CLI process. For any non-web application, use **username/password
authentication** instead — don't reach for JWT, OAuth, or any token scheme
here.

Minimum viable implementation for the example app:

- Prompt for a username and password before the `add` command (and any other
  mutating command) will run. Use a console-based masked-input read (e.g.
  `java.io.Console#readPassword`, which returns a `char[]` you can wipe after
  use) rather than reading the password as plain `String` from `args` or
  standard input — arguments are visible in shell history and process
  listings, which defeats the point.
- Store credentials for the example as a small in-memory user store (e.g. one
  hardcoded demo user, or a `Map<String, String>` of username → password
  hash), consistent with the "no external storage" constraint elsewhere in
  this skill. **Never store the password itself** — hash it (e.g.
  `java.security.MessageDigest` with SHA-256 plus a per-user salt, or a
  proper password-hashing library like `at.favre.lib:bcrypt` if you want to
  bring in a dependency for it) and compare hashes on login.
- If the selected CLI framework has its own idiomatic way to gate a command
  behind a login step (e.g. Spring Shell's method-availability/interactivity
  hooks, or a picocli `@Command` that runs an interactive login prompt before
  dispatching to subcommands), use that instead of a generic hand-rolled gate.
- If the CLI calls a remote HTTP API on the user's behalf as part of its
  actual function, still authenticate the *CLI's own* user with
  username/password locally, and only introduce a token for the outbound
  call if the remote API specifically requires one — don't let that turn the
  CLI's own auth into JWT by the back door.

State in the generated README exactly what was implemented (which command(s)
require login, where/how credentials are stored and hashed) so the user
isn't surprised by what "security layer" means for this CLI.

## Web apps use JWT (see above); everything else uses username/password

This section exists so the choice is unambiguous when Step 8 is reached:
**web application → JWT** (previous section); **anything that is not a web
application → username/password**, as described here. Don't mix the two
based on incidental features (e.g. a CLI that happens to make HTTP calls is
still a CLI for this purpose, not a web application).
