# IoTFlow - Artifact

## Overview

![Overview of IoTFlow](iotflow_figure.svg)

We use VSA to reconstruct endpoints, cryptographic data, and ICC keys for the flow analysis. We use flow analysis to find data leaks, and connect request/response data with endpoints. With the ICC information of the VSA, we support data flows involving ICC.

For more details, see [our paper "IoTFlow: Inferring IoT Device Behavior at Scale through Static Mobile Companion App Analysis"](./iotflow_paper.pdf) we presented at CCS 2023.

## Folder Structure

* [VSA](VSA/) contains the code of the value set analysis. We provided a [Docker container](VSA/docker/) to run it. Add apps to `apps_to_analyze` and hit `docker compose up` to try it out.
* [FlowAnalysis](FlowAnalysis/) contains the code of the data flow analysis. We again provided a [Docker container](FlowAnalysis/docker/apps_to_analyze/) for easier setup. Add apps to [apps_to_analyze](FlowAnalysis/docker/apps_to_analyze/) and hit `docker compose up` to try it out.
* In [config](config/) we provide the configurations we used for the analysis, e.g., the sources and sinks.
* [Datasets](datasets/) contain the app ids and version codes of the apps we used.
* In [scripts](scripts/) we added code, we used to analyze the obtained results further and generate the tables.

## Local changes (2026-11)

Changes to keep the Docker setup working with current systems and apps:

- **Base images:** `debian:11-slim` can no longer install OpenJDK because its security repository is gone. The VSA image now uses `eclipse-temurin:11-jre`. The flow-analysis image uses `python:3.9-slim-bookworm` with `openjdk-17-jre-headless`, and installs the Python dependencies before copying scripts so rebuilds reuse the cache.
- **dex2jar:** 2.1 produced an empty jar for any APK. It is replaced by [dex2jar 2.4.38](https://github.com/ThexXTURBOXx/dex2jar), the maintained fork; only the parts that are used are kept. Converting a large app takes several minutes, but it happens only once per app (`apps_to_analyze/jarFiles/`).
- **Large multi-DEX apps:** dex2jar fails on some of them when converting the whole APK (e.g. `com.tplink.iot`, 18 DEX files: `OutOfMemoryError` even with 16 GB), leaving a 22-byte placeholder jar that the VSA silently reuses. Convert every app beforehand with `scripts/apk2jar.sh <apk>`: it converts one DEX file at a time and merges the result into both `jarFiles/` folders. dex2jar's heap is now 8 GB (`D2J_XMX` in `d2j_invoke.sh`).
- **VSA analyses:** `VSA/docker/execute_vsa.sh` runs endpoints, crypto, mqtt, udp and webview (override with `-e ANALYSES=...`). coap, amqp and xmpp are run by the FlowAnalysis stage.
- **FlowDroid resource parser:** patched so apps built with recent Android build tools no longer crash with "res1 was not zero". See [patches/arsc-typescount](patches/arsc-typescount/).
- **Call-graph errors:** Soot 4.4.1 aborted whole FlowDroid runs on single methods it could not type ("Attempt to create VarNode of type boolean"). Patched to log and skip such methods. See [patches/allow-cg-errors](patches/allow-cg-errors/).
- **IoTScope `VerifyError`:** IoTScope runs with `-XX:+UnlockDiagnosticVMOptions -XX:-BytecodeVerificationRemote`, because some dex2jar-converted classes fail Java's bytecode verifier and aborted the analysis.
- **Removed:** `FlowAnalysis/docker/dependencies/InstrumentationAgent.jar`, which the flow analysis never used.
- **Memory:** `FlowAnalysis/docker/execute_iotflow.sh` uses `-mmf 8 -mmi 4`, because the first stage runs two VSA JVMs and FlowDroid at the same time.
- **Logs:** Docker log files are capped (`compose.yaml`), because the analysis logs millions of lines per hour.
- **Faster runs:**
  - `VSA/docker/execute_vsa.sh` runs only the `endpoints`, `crypto`, `mqtt` and `udp` analyses. Add `amqp`, `coap`, `xmpp` or `webview` back to `ANALYSES` if needed.
  - Both tools log at `warn` level (`-Dorg.slf4j.simpleLogger.defaultLogLevel=warn`) instead of `info`.
  - The VSA skips generic third-party libraries listed in `config/exclude.json`: AndroidX, RxJava, BouncyCastle, Material, Protobuf, Gson, Guava and others. This list is also passed by `FlowAnalysis/docker/scripts/iotflow.py`, and copied to `FlowAnalysis/docker/config/iotscope/exclude.json`. Networking libraries, vendor SDKs, maps and Google Play services are not excluded. Review the list for each new app, so that no library that builds network requests is excluded.
- **Git:** `.gitignore` excludes `*.xapk` and the APKs in `apps_to_analyze/`.



## How to cite:

```
@inproceedings{iotflow:ccs2023,
  title     = {{IoTFlow: Inferring IoT Device Behavior at Scale through Static Mobile Companion App Analysis}},
  author    = {Schmidt, David and Tagliaro, Carlotta and Borgolte, Kevin and Lindorfer, Martina},
  booktitle = {Proceedings of the 30th ACM SIGSAC Conference on Computer and Communications Security (CCS)},
  date      = {2023-11},
  doi       = {10.1145/3576915.3623211},
  edition   = {30},
  editor    = {Cremers, Cas and Kirda, Engin},
  location  = {Copenhagen, Denmark},
  publisher = {Association for Computing Machinery (ACM)},
}
```

## Contacts
* David Schmidt:
    * email: dschmidt@seclab.wien
    * bsky: @dschm1dt.bsky.social
    * twitter: @dschm1dt
* Carlotta Tagliaro:
    * email: carlotta@seclab.wien
    * twitter: @Pseudorandomico
* Kevin Borgolte
    * email: kevin.borgolte@rub.de
    * twitter: @caovc
* Martina Lindorfer
    * email: martina@seclab.wien
    * twitter: @lindorferin
