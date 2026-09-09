# GitHub Actions CI/CD

Generate `.github/workflows/ci.yml`. Adapt the skeleton below to the actual
selections made earlier in the workflow — don't hardcode a Java version or
build type the user didn't choose.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK <SELECTED_JDK_MAJOR>
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "<SELECTED_JDK_MAJOR>"

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      # Only include if Playwright E2E tests were added (Step 11):
      - name: Install Playwright browsers
        run: ./gradlew playwrightInstall   # or `npx playwright install --with-deps`,
                                            # matching however Playwright was wired in

      - name: Build, test, and run code quality checks
        run: ./gradlew build check

      - name: Upload quality reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-reports
          path: |
            build/reports/checkstyle/
            build/reports/pmd/
            build/reports/spotbugs/
            build/reports/tests/
            build/reports/jacoco/   # if JaCoCo was added

  # Only include the job below if a Docker build type was selected (Step 12):
  docker-image:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK <SELECTED_JDK_MAJOR>
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "<SELECTED_JDK_MAJOR>"
      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
      - name: Build container image
        run: ./gradlew <the framework-specific image task, e.g. bootBuildImage / quarkusBuild --docker / dockerBuild>

  # Only include the job below if a native-image build type was selected (Step 12):
  native-image:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up GraalVM
        uses: graalvm/setup-graalvm@v1
        with:
          java-version: "<SELECTED_JDK_MAJOR>"
          distribution: "graalvm"
      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
      - name: Build native image
        run: ./gradlew nativeCompile   # or the framework-specific native task
```

Before finalizing, discover the current stable major version of each action
used (`actions/checkout`, `actions/setup-java`, `gradle/actions/setup-gradle`,
`actions/upload-artifact`, `graalvm/setup-graalvm`) rather than trusting the
version numbers above — treat them the same as any other dependency under
the discover/verify discipline, since GitHub Actions versions this
independently of everything else in the project.

Keep the three jobs conditional on what was actually selected — a project
with no Docker/native build type shouldn't ship a workflow with dead jobs
that will fail for lack of a corresponding Gradle task.
