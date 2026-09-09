#!/usr/bin/env bash
# Verifies that a JDK of the required major version and a Gradle install are
# present on the local PATH before the skill scaffolds a project. The
# generated project ships its own Gradle wrapper for day-to-day builds, but
# the skill needs a real local JDK (and, for the first-ever wrapper
# invocation, a bootstrap Gradle or an already-cached wrapper distribution)
# to validate the scaffold it just created.
#
# Usage: verify_environment.sh <required-java-major> [required-gradle-version]
#
# Exit codes:
#   0 - both checks passed (or the Gradle check was skipped because no
#       required version was given)
#   1 - required Java major version not found / no `java` on PATH
#   2 - `gradle` not found on PATH (only checked if arg 2 is given)
#   3 - usage error

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <required-java-major> [required-gradle-version]" >&2
  exit 3
fi

REQUIRED_JAVA_MAJOR="$1"
REQUIRED_GRADLE_VERSION="${2:-}"

fail() {
  echo "ERROR: $1" >&2
  exit "$2"
}

if ! command -v java >/dev/null 2>&1; then
  fail "No 'java' executable found on PATH. Install a JDK $REQUIRED_JAVA_MAJOR (Temurin/Eclipse Adoptium, or your preferred vendor) before continuing." 1
fi

# `java -version` prints to stderr; formats vary ("21.0.4", "25", "1.8.0_402").
RAW_VERSION="$(java -version 2>&1 | head -n 1)"
VERSION_STRING="$(echo "$RAW_VERSION" | grep -oE '"[^"]+"' | tr -d '"')"

if [[ -z "$VERSION_STRING" ]]; then
  fail "Could not parse Java version from: $RAW_VERSION" 1
fi

if [[ "$VERSION_STRING" == 1.* ]]; then
  # Legacy "1.8.0_402" style versioning.
  DETECTED_MAJOR="$(echo "$VERSION_STRING" | cut -d. -f2)"
else
  DETECTED_MAJOR="$(echo "$VERSION_STRING" | cut -d. -f1)"
fi

if [[ "$DETECTED_MAJOR" != "$REQUIRED_JAVA_MAJOR" ]]; then
  fail "Detected Java major version $DETECTED_MAJOR (full: $VERSION_STRING), but this project requires Java $REQUIRED_JAVA_MAJOR. Install JDK $REQUIRED_JAVA_MAJOR and make sure it is first on PATH (or configure a Gradle toolchain pointing at it) before continuing." 1
fi

echo "OK: Java $VERSION_STRING satisfies the required major version $REQUIRED_JAVA_MAJOR."

if [[ -n "$REQUIRED_GRADLE_VERSION" ]]; then
  if ! command -v gradle >/dev/null 2>&1; then
    fail "No 'gradle' executable found on PATH. A local Gradle install (>= $REQUIRED_GRADLE_VERSION) is needed to bootstrap the wrapper and run the first validation build. Install it (e.g. via sdkman: 'sdk install gradle $REQUIRED_GRADLE_VERSION') before continuing." 2
  fi
  DETECTED_GRADLE="$(gradle --version 2>&1 | grep -m1 '^Gradle' | awk '{print $2}')"
  echo "OK: found local Gradle $DETECTED_GRADLE (required >= $REQUIRED_GRADLE_VERSION — confirm this satisfies the compatibility matrix looked up in Step 5 before proceeding)."
fi

exit 0
