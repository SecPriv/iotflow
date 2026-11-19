# Validation: FlowDroid 2.15.1 port vs. FlowDroid 2.12 (IoTFlow original)

**App:** `com.rainbow.drone` 5.15 (base APK). **Date:** 2026-11-19.
**Setup:** FlowAnalysis stage only, `MMF=8 MMI=4` (same as the 2.12 run of 2026-11-18). The VSA results of the 2.12 run (`sources`, `sinks`, `endpoints`, `udp`, `mqtt`, `amqp`, `coap`, `xmpp`) were copied in, so only the FlowDroid runs differ.
**Run time:** 42 min (2.12: about 29 min).

| Result file | 2.12 state | flows | 2.15.1 state | flows | common | runtime 2.12 / 2.15.1 |
|---|---|---|---|---|---|---|
| `bl_to_icc_or_sink` | Success | 0 | Success | 0 | 0 | 273 / 344 s |
| `both/web_okhttp3` | Success | 17 | Success | 19 | 17 | 256 / 361 s |
| `both/web_udp_data` | Success | 0 | Success | 0 | 0 | 239 / 372 s |
| `general_to_icc_or_sink` | Success | 2 | **DataFlowOutOfMemory** | 3 | 2 | 267 / 485 s |
| `sink_connection/web_java` | Success | 0 | Success | 0 | 0 | 247 / 353 s |
| `source_connection/web_java` | Success | 0 | Success | 0 | 0 | 239 / 314 s |
| all other files | empty (no applicable sources/sinks) | | empty | | | |

**Total:** 2.12 = 19 flows, 2.15.1 = 22 flows, **all 19 of 2.12 also found by 2.15.1**, none lost.

Only in 2.15.1:
- `both/web_okhttp3`: `okhttp3.Request$Builder.url(String)` → `okhttp3.Call.enqueue` in `mobi.heyemoji.drone.util.e.q0(...)` (the app's own code)
- `both/web_okhttp3`: `Request$Builder.url(HttpUrl)` → `Call.enqueue` (inside OkHttp)
- `general_to_icc_or_sink`: `Locale.getCountry()` → `SharedPreferences$Editor.putString` in `zk$b.t()`

## Findings

1. **Results:** superset of 2.12 on this app; the extra flows are plausible (an additional OkHttp request in the app's code).
2. **Memory and time:** 2.15.1 needs more of both, 20–80 % more time per FlowDroid run. `general_to_icc_or_sink` ran out of memory at 8 GB (`TerminationState=DataFlowOutOfMemory`), so its result is partial even though it already contains the 2.12 flows. Use a larger `MMF` with 2.15.1 (e.g. 12 GB on this 30 GB machine, 30 GB on the 64 GB laptop).
3. **Path reconstruction** was much slower in a Shelly smoke test (722 s vs. 57 s); not limited by IoTFlow's `-ct`/`-dt` timeouts. Consider FlowDroid's result-collection timeout (`-rt`).
4. **Command line:** `-d` (`--mergedexfiles`) removed in 2.15 (Soot 4.7 always loads all DEX files); IoTFlow no longer passes it.
