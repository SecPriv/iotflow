# Local changes (2026-11)

Changes to the original IoTFlow artifact, to keep it working with current systems and apps. The newest are at the top of each section.

## Analysis tools

- **FlowDroid 2.15 regression: services without their own `onBind()`** (2026-11-19): FlowDroid 2.15 tried to add a body to the abstract `android.app.Service.onBind()` and aborted every run on WiZ (which bundles an empty stub of a framework service class). Fixed in a replacement `ServiceEntryPointCreator` in `FlowAnalysis/src`; not fixed upstream. See [patches/service-onbind](patches/service-onbind/).
- **FlowDroid 2.15.1 / Soot 4.7.1 in the flow analysis** (2026-11-19; developed on branch `flowdroid-2.15-upgrade`):
  - **Why:** Soot 4.4.1 (FlowDroid 2.12) aborted FlowDroid runs on modern apps while building the call graph (`Attempt to create VarNode of type boolean`, from failed DEX typing of R8-optimised code). Soot 4.7's DEX typing does not hit it, and FlowDroid 2.14+ parses the new ARSC format natively.
  - **Validation:** on `com.rainbow.drone`, all 19 flows of the old version are found again, plus 3 new ones; 2.15.1 needs more memory and 20–80 % more time per run. See [patches/VALIDATION-flowdroid-2.15.md](patches/VALIDATION-flowdroid-2.15.md).
  - **Ported IoTFlow classes:**
    - `SummaryTaintWrapper`: the 2.15.1 file plus IoTFlow's try/catch.
    - XML source/sink parser: three-way merge. IoTFlow's `customId` attribute is accepted and ignored (it was always `WHATEVER`).
    - `CustomSetupApplication`: `File`-based API.
    - `LocationSourceSinkManager`: location filter applied per definition.
  - FlowDroid's `-d` (`--mergedexfiles`) option no longer exists (Soot 4.7 always loads all DEX files) and is no longer passed.
  - Build: see [FlowAnalysis/README.md](FlowAnalysis/README.md).
  - The VSA (IoTScope, also used inside the flow stage via `dependencies/vsa.jar`) stays on FlowDroid 2.12 / Soot 4.4.1.
- **VSA `VerifyError`** (2026-11-19): some dex2jar-converted classes fail Java's bytecode verifier; the `VerifyError` ended the whole VSA analysis. Patched to skip the affected backward path instead. See [patches/vsa-linkage-errors](patches/vsa-linkage-errors/). (Turning verification off made the JVM crash.)
- **Call-graph errors in FlowDroid 2.12** (2026-11-19): patched to log and skip methods Soot cannot type. See [patches/allow-cg-errors](patches/allow-cg-errors/). Now only relevant for the VSA jars.
- **FlowDroid resource parser** (2026-11-18): patched so apps built with recent Android build tools no longer crash with "res1 was not zero". See [patches/arsc-typescount](patches/arsc-typescount/). Now only relevant for the VSA jars.
- **dex2jar** (2026-11-18): 2.1 produced an empty jar for any APK. Replaced by [dex2jar 2.4.38](https://github.com/ThexXTURBOXx/dex2jar), the maintained fork; only the parts that are used are kept.
  - dex2jar fails on some large multi-DEX APKs when converting the whole APK (e.g. `com.tplink.iot`, 18 DEX files) and leaves a 22-byte placeholder jar that the VSA silently reuses. Convert every app beforehand with `scripts/apk2jar.sh` (one DEX file at a time).
  - dex2jar's heap: 8 GB (`D2J_XMX` in `d2j_invoke.sh`).

## Running

- **One Compose project, shared dependencies, results owned by the user** (2026-11-19):
  - A single top-level `compose.yaml` (project `iotflow`) with the services `vsa` and `dfa` replaces the two per-stage compose files.
  - `vsa.jar`, `android-31.jar`, dex2jar and the instrumentation agent are in one top-level `dependencies/` folder, mounted read-only into both containers. Before, each image had its own copy and every patch had to be applied twice.
  - The containers run as `HOST_UID:HOST_GID` (set by `run_pipeline.sh` to the calling user), so results no longer belong to root.
  - `.dockerignore` files keep `apps_to_analyze/` and `results/` (several GB) out of the image build context.
- **Flow stage reuses VSA results** (2026-11-19): `run_pipeline.sh` copies the VSA stage's endpoints/mqtt/udp results (same configuration, same jar) to the flow stage, which then skips computing them again.
- **Quieter logs** (2026-11-19): IoTScope's simulation (`iotscope.forwardexec`), backward slicing and resource lookups are switched off. They produced >99 % of all log lines (about 11 million for three apps); a test on `com.rainbow.drone` gave the same 42 value points and 63 URLs with and without them. Soot's `Failed Typing` errors and all fatal errors are kept.
- **Summary per app** (2026-11-19): `scripts/summarize.py <package>` writes a Markdown summary (status, errors, endpoints by host, crypto/UDP/MQTT/WebView values, flows). `scripts/reset_incomplete.py` resets FlowDroid runs that ran out of memory so only those are repeated.
- **Stop on fatal errors** (2026-11-19): a Java process that hits an uncaught exception in its main thread, a JVM crash, an `OutOfMemoryError` or a FlowDroid abort ("The data flow analysis has failed") usually writes no results but keeps running until its timeout. Both stages now stop such a process 5 s after the error line (so the stack trace is still logged) and continue with the next task:
  - VSA (`VSA/docker/execute_vsa.sh`): error line and stack trace in `results/<analysis>/<package>.error`; later passes skip that analysis (delete the file to retry). The VSA uses the Parallel GC, so a heap that is too small ends with `OutOfMemoryError: GC overhead limit exceeded` instead of hours of garbage collection.
  - Flow stage (`FlowAnalysis/docker/scripts/iotflow.py`, `start_guarded`): FlowDroid and IoTScope processes; causes in `results/errors/<package>.log`. FlowDroid's own memory stop ("Running out of memory, solvers terminated") is not treated as fatal, because it still writes partial results.
- **Faster VSA stage** (2026-11-20):
  - **Parallel apps:** apps whose converted jar is under `VSA_SMALL_MB` (100 MB) run up to `VSA_PARALLEL` at a time with heap `VSA_XMX_SMALL`; large apps follow one at a time with `VSA_XMX`. Log lines are tagged `[<package>/<analysis>]`; the fatal-error stop kills only the affected JVM (before: all Java processes in the container).
  - **Pass 2 skipped after a pass-1 timeout:** pass 2 (without the agent) is not faster; pass 3 (shorter backward paths) follows directly. Saves up to one `VSA_TIMEOUT` per analysis on large apps. Passes now run per analysis (1, 2, 3 for endpoints, then for crypto, ...) instead of pass 1 for all analyses first.
  - **`<package>.timeout` marker** when the last pass also hit the time limit (like `.error`; delete to retry).
  - **Flow stage skips what the VSA had to stop:** `run_pipeline.sh` copies `.error`/`.timeout` markers of endpoints/mqtt/udp/amqp/coap/xmpp as `<package>.vsa-error`/`.vsa-timeout` to the flow stage's results, and `iotflow.py` skips that IoTScope analysis (it would fail again with less memory). `summarize.py` shows both.
- **VSA image on Java 17** (2026-11-20): runs both the current `vsa.jar` and the Soot 4.7.1 port. Tested on drone and eWeLink against the Java 11 results: same value points in all 10 analyses, 6 identical; the others differ by a few values, like two runs of the same setup (eWeLink endpoints is not deterministic). Not above 17: the VSA uses `Thread.stop()`. `scripts/vsa_version.sh` switches between the two VSA versions (`dependencies/vsa-soot-4.7/`).
- **Run settings as environment variables** (2026-11-18/19), passed through the top-level `compose.yaml`: `ANALYSES`, `VSA_XMX`, `VSA_XMX_SMALL`, `VSA_PARALLEL`, `VSA_SMALL_MB`, `VSA_TIMEOUT`, `VSA_EXCLUDE`, `D2J_XMX` (VSA); `MMF`, `MMI`, `IOTSCOPE_EXCLUDE` (flow stage). See the tables in [VSA/docker/README.md](VSA/docker/README.md) and [FlowAnalysis/docker/README.md](FlowAnalysis/docker/README.md).
- **Detached pipeline** (2026-11-18): `scripts/run_pipeline.sh` runs the VSA, then the flow analysis, independent of the terminal. See [scripts/README.md](scripts/README.md).
- **VSA analyses:** `endpoints crypto mqtt udp webview` by default. `amqp`, `coap` and `xmpp` are run by the flow stage, so they are not repeated in the VSA stage; `webview` is run by neither stage otherwise.
- **Exclusion lists:** the VSA skips generic third-party libraries (`VSA/docker/config/exclude.json`, copied to `FlowAnalysis/docker/config/iotscope/exclude.json`): AndroidX, RxJava, BouncyCastle, Material, Protobuf, Gson, Guava and others. Networking libraries, vendor SDKs, maps and Google Play services are not excluded. `exclude_large.json` additionally skips more libraries for very large apps. Never exclude an app's own code; its package can differ from the app id.
- **Logs:** both tools log at `warn` level instead of `info`; Docker log files are capped (`compose.yaml`); `run_pipeline.sh` drops the two noisiest warning types.
- **Memory:** `FlowAnalysis/docker/execute_iotflow.sh` defaults to `-mmf 8 -mmi 4`, because the flow stage runs two VSA JVMs and FlowDroid at the same time; override with `MMF` / `MMI`.

## Docker images

- **Base images** (2026-11-18): `debian:11-slim` can no longer install OpenJDK because its security repository is gone. The VSA image uses `eclipse-temurin:11-jre`; the flow-analysis image uses `python:3.9-slim-bookworm` with `openjdk-17-jre-headless`, and installs the Python dependencies before copying the scripts so rebuilds reuse the cache.
- **Compose project names** (`iotflow-vsa`, `iotflow-dfa`): both compose files live in a folder called `docker` and would otherwise share one Compose project.

## Clean-up (2026-11-19)

- **Removed** the top-level `config/` folder: all 309 files were identical copies of `VSA/docker/config/` and `FlowAnalysis/docker/config/` (with different folder names). Its description of the sources and sinks moved to [FlowAnalysis/docker/config/README.md](FlowAnalysis/docker/config/README.md).
- **Removed** `scripts/run/`: an older copy of `FlowAnalysis/docker/scripts/` that had none of the fixes. How to run `iotflow.py` without Docker: [scripts/README.md](scripts/README.md).
- **Removed** `FlowAnalysis/docker/scripts/local_to_remote.py` (unused, only an empty function) and `FlowAnalysis/docker/dependencies/InstrumentationAgent.jar` (never used by the flow analysis).
- **APK upload is opt-in:** `iotflow.py` used to upload every APK to `http://apk-deguard.com/upload` (third party, plain HTTP) for deobfuscation unless `-sd` was passed. It now does so only with `--deguard`; `-sd` is still accepted.
- **Fixed** copy-pasted help texts in `iotflow.py` and the title of `FlowAnalysis/docker/README.md`.
- **Documented** that `VSA/src` does not match the `vsa.jar` that is run ([VSA/README.md](VSA/README.md)).
- **Git:** `.gitignore` excludes `*.xapk`, the APKs in `apps_to_analyze/`, `apps/` and Gradle caches.
- **Scripts mounted into the containers** (2026-11-24): `compose.yaml` mounts the stage scripts and `iotflow.jar` from the folder, so changes apply without rebuilding; `scripts/run_pipeline.sh` uses the existing image if the build fails (e.g. no internet). A 0-byte result file is no longer taken as a result (`execute_vsa.sh`, `run_pipeline.sh`, `iotflow.py`).
