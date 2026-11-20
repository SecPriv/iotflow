# Value Set Analysis

* [Dockerized](docker/) analysis, for simpler execution.

> **This branch (`vsa-soot-upgrade`):** the VSA runs on FlowDroid 2.15.1 / Soot 4.7.1 and Java 17. `src/` is the revision the original `vsa.jar` was built from (commit `8609458`; the later "cleaned up" source was never used in a run), ported to the new Soot. Details and validation: [`patches/VALIDATION-vsa-soot-4.7.md`](../patches/VALIDATION-vsa-soot-4.7.md).


Example usage:
```
java -Xms5g -Xmx16g -jar IoTScope.jar -d config/xmpp.json -p ~/Android/Sdk/platforms/ -o /outputPath/ -t config/taintrules.json -a app.apk -dj dex_tools_2.4.38/d2j-dex2jar.sh
```

IoTScope -a <apk to analyse> -d <description of methods (sources)> -dj <dex2jar path>  -p <Android jar file or platform directory>  -t <taint rule file> [-o <output folder>] [-e <exclusion list file>] [-mb <number of steps it should trace backward>] [-mbc <number of backward context it should create>] [-og [-ogp <output path for dot files>]]  [-tb <Timeout backward tracing in minutes>] [-tf <Timeout forward computation in minutes>] [-do] [-obc]  [-oj]

Required arguments:
-a Apk file to analyze
-d list of signatures to trace
-dj dex2jar analysis path. Dex2Jar can be downloaded from there repository: https://github.com/pxb1988/dex2jar
-p Android jar file path, or Android platforms directory path.
-t taint rule file, a minimal file only contains

Option arguments
-o output folder path
-e list of paths in apk to exclude
-mb maximum steps backward per context
-mbc maximum number of backward context, each branch is an own context
-tb timeout backward in minutes
-tf timeout forward computation in minutes
-do don't overwrite results flag
-obc output backward context to results flag
-oj output jimple flag
-og output the call graph flag
    -ogp output paths for the graphs dot files

If the analysis run out of memory, reduce the number of backward context `-mbc`, and steps back `-mb`, the available memory to the jvm can be controlled via `-Xmx`.

## Building (Gradle 8, Java 17, in Docker)

From `VSA/`:
```bash
docker run --rm -u $(id -u):$(id -g) -e GRADLE_USER_HOME=/w/.gradle-home -v $PWD:/w -w /w \
    gradle:8.10.2-jdk17 gradle --no-daemon shadowJar :InstrumentationAgent:shadowJar
```
Results: `build/libs/vsa.jar` and `InstrumentationAgent/build/libs/InstrumentationAgent.jar` (copy them into `docker/` and `docker/dependencies/`). To rebuild the old Soot 4.4.1 version for comparisons, add `-PflowdroidJar=libs/soot-infoflow-cmd-jar-with-dependencies.jar -PjavaRelease=11`.

## Instrumentation Agent
The instrumentation agent is optional. It can add `toString`, `equals`, and `hashCode` methods to classes during the analysis execution. That can help to remove duplicates and reduce the required memory. To execute the value set analysis with the agent add `-javaagent:[path_to_instrumentation_agent.jar]` to the command
