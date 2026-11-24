# Shared dependencies

Mounted read-only into both containers (see the top-level `compose.yaml`): at `/vsa/dependencies` (VSA) and `/analysis/dependencies` (flow analysis).

| File | Used by | Notes |
|---|---|---|
| `vsa.jar` | VSA stage; IoTScope runs inside the flow stage | IoTScope, patched (see `../patches/`). Built from a different source version than `VSA/src` (see `VSA/README.md`). |
| `android-31.jar` | both | Android platform classes for Soot / FlowDroid |
| `dex_tools_2.4.38/` | both | dex2jar 2.4.38 (ThexXTURBOXx fork); heap via `D2J_XMX`. Prefer `scripts/apk2jar.sh` on the host. |
| `InstrumentationAgent.jar` | VSA stage (first pass) | Adds `toString`/`equals`/`hashCode` to simulated classes; source in `VSA/InstrumentationAgent/` |
| `vsa-soot-4.7/` | – | `vsa.jar` + agent ported to FlowDroid 2.15.1 / Soot 4.7.1 (branch `vsa-soot-upgrade`), for testing. `scripts/vsa_version.sh 4.7` copies them into place (and saves the current ones to `vsa-soot-4.4/`); `scripts/vsa_version.sh 4.4` switches back. |

Patches are applied once, here (there used to be one copy per image).
