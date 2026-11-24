# Docker setup: value set analysis (VSA)

Usually started together with the flow analysis by `scripts/run_pipeline.sh` (see the main [README](../../README.md)). To run this stage alone:

1. Put the base APKs into `apps_to_analyze/` and convert them first: `scripts/apk2jar.sh VSA/docker/apps_to_analyze/<app>.apk` (from the repository root).
2. From the repository root: `HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up --build vsa` (add `-d` to run in the background). Without `HOST_UID`/`HOST_GID` the container runs as root and the results belong to root.
3. Results: `results/<analysis>/<package>.json`, one folder per analysis (`endpoints`, `crypto`, `mqtt`, `udp`, `webview`).
   - An analysis that stopped with a fatal error leaves `results/<analysis>/<package>.error` (error line and stack trace); one whose last pass hit the time limit leaves `<package>.timeout`. Later passes and runs skip it, and so does the flow stage (it would only fail again with less memory). Delete the file to retry.

## Passes

Each analysis runs up to three passes until one produces a result: (1) with the instrumentation agent, (2) without it, (3) without it and with shorter backward paths (`-mb 20 -mbc 100`). Pass 2 is skipped if pass 1 hit the time limit, because it is not faster; it only helps when the agent itself causes a problem.

## Parallel runs

Apps whose converted jar is smaller than `VSA_SMALL_MB` run up to `VSA_PARALLEL` at a time, each with heap `VSA_XMX_SMALL`; larger apps (and apps without a jar yet) run afterwards one at a time with `VSA_XMX`. The VSA uses about one CPU core per app, so parallel runs are limited by memory, not CPU: plan about `VSA_PARALLEL × VSA_XMX_SMALL` + 1 GB per JVM. Every log line is tagged `[<package>/<analysis>]`. A fatal error stops only the JVM of that app and analysis.

On a 64 GB machine: `VSA_PARALLEL=3 VSA_XMX_SMALL=16g VSA_XMX=44g`. The small apps so far peaked at 5–13 GB per analysis with a 12–16 GB heap.

## Settings

Environment variables, passed through the top-level `compose.yaml` (unset = default), e.g. `ANALYSES=endpoints VSA_TIMEOUT=2h docker compose up --build vsa`:

| Variable | Default | Meaning |
|---|---|---|
| `ANALYSES` | `endpoints crypto mqtt udp webview` | Analyses to run (config files in `config/`) |
| `VSA_XMX` | `16g` | Java heap (large apps; also small apps unless `VSA_XMX_SMALL` is set) |
| `VSA_XMX_SMALL` | `VSA_XMX` | Java heap for small apps |
| `VSA_PARALLEL` | `1` | Small apps analysed at the same time |
| `VSA_SMALL_MB` | `100` | Size limit of the converted jar (`jarFiles/<package>-dex2jar.jar`) for "small" |
| `VSA_TIMEOUT` | `40m` | Time limit per analysis pass (Java then gets 5 more minutes to stop) |
| `VSA_EXCLUDE` | `/vsa/config/exclude.json` | Exclusion list of third-party packages; `/vsa/config/exclude_large.json` for very large apps |
| `D2J_XMX` | `8g` | dex2jar heap (only if a jar is converted inside the container) |

Everything else (passes, `-mb`/`-mbc` cut-offs, Java and log options) is in `execute_vsa.sh`. `vsa.jar`, `android-31.jar`, dex2jar and the instrumentation agent are in the shared top-level [`dependencies/`](../../dependencies/) folder, mounted read-only into the container.
