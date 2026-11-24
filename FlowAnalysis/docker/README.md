# Docker setup: flow analysis (FlowDroid 2.15.1 + IoTScope)

Usually started after the VSA by `scripts/run_pipeline.sh` (see the main [README](../../README.md)). To run this stage alone:

1. Put the base APKs into `apps_to_analyze/` and their jars into `apps_to_analyze/jarFiles/` (`scripts/apk2jar.sh` does both stages at once).
2. From the repository root: `HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up --build dfa` (add `-d` to run in the background). Without `HOST_UID`/`HOST_GID` the container runs as root and the results belong to root.
3. Results in `results/`:
   - IoTScope (VSA) results: `sources/`, `sinks/`, `endpoints/`, `udp/`, `mqtt/`, `amqp/`, `coap/`, `xmpp/` (`<package>.json`)
   - FlowDroid results: `bl_*`, `general_*`, `local_*` (Bluetooth, general and local-network runs), `both/`, `sink_connection/`, `source_connection/` (`<package>.xml`)
   - `errors/<package>.log`: processes stopped because of a fatal error, with the stack trace

## Settings

Environment variables, passed through the top-level `compose.yaml` (unset = default), e.g. `MMF=30 MMI=12 docker compose up --build dfa`:

| Variable | Default | Meaning |
|---|---|---|
| `MMF` | `8` | FlowDroid heap in GB (2.15.1 needs more than 2.12; 12 on a 30 GB machine, 30 on 64 GB) |
| `MMI` | `4` | Heap in GB for each IoTScope JVM (up to two run next to FlowDroid) |
| `IOTSCOPE_EXCLUDE` | `/analysis/config/iotscope/exclude.json` | Exclusion list for IoTScope; `.../exclude_large.json` for very large apps |

FlowDroid timeouts and other options: `execute_iotflow.sh` and `scripts/iotflow.py --help`. IoTScope (`vsa.jar`), `android-31.jar` and dex2jar are in the shared top-level [`dependencies/`](../../dependencies/) folder, mounted read-only into the container. Deobfuscation via the online service apk-deguard.com is off; `--deguard` turns it on (uploads the APK to a third party).
