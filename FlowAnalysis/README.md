# Data Flow Analysis

* [Dockerized](docker/) analysis execution.
* **FlowDroid version:** 2.15.1 with Soot 4.7.1 (`libs/soot-infoflow-cmd-2.15.1-jar-with-dependencies.jar`, from Maven Central), since 2026-11-19.
  - The original IoTFlow used a 2023 FlowDroid snapshot ([commit 542ff86](https://github.com/secure-software-engineering/FlowDroid/tree/542ff865f87a1da5b8fd63ea89ffffa03e6b56e5)), chosen because of [FlowDroid issue #593](https://github.com/secure-software-engineering/FlowDroid/issues/593) and [#596](https://github.com/secure-software-engineering/FlowDroid/issues/596).
  - Its Soot 4.4.1 aborted the analysis of modern apps while building the call graph. The port and its validation (all flows of the old version found again on `com.rainbow.drone`) are described in [`../patches/VALIDATION-flowdroid-2.15.md`](../patches/VALIDATION-flowdroid-2.15.md).
  - Whether #593 / #596 still occur in 2.15.1 was not checked separately.

## Changes to the FlowDroid source code (`src/`, classes replacing FlowDroid's own)

* Sources and sinks parser with an optional location in the bytecode, so that only specific statements are considered (`CustomXMLSourceSinkParser`, `CustomAbstractXMLSourceSinkParser`, `CustomXMLConstants`)
* Source and sink manager that only returns sources and sinks if the location matches (`LocationSourceSinkManager`)
* Custom `Main`, `CustomSetupApplication` and `SummaryTaintWrapper` to use the custom parser and manager; the taint wrapper ignores failing summary lookups
* `ServiceEntryPointCreator`: fix for a FlowDroid 2.15 regression with services that do not implement `onBind()` themselves (see `../patches/service-onbind/`)

## Building

Java 17, Gradle 8.10.2, in Docker (no local JDK 17 needed), from `FlowAnalysis/`:

```bash
docker run --rm -u $(id -u):$(id -g) -e GRADLE_USER_HOME=/w/.gradle-home -v $PWD:/w -w /w \
  gradle:8.10.2-jdk17 gradle --no-daemon shadowJar
cp build/libs/iotflow.jar docker/iotflow.jar
```
