# Validation: VSA on FlowDroid 2.15.1 / Soot 4.7.1

Branch `vsa-soot-upgrade`, 2026-11-20. Compares three VSA jars on two apps, all five analyses.

## Jars

| Name | What | Soot |
|---|---|---|
| **orig** | `vsa.jar` used in all runs so far (with the bytecode patches in `patches/`) | 4.4.1 (FlowDroid 2.12) |
| **baseline** | built from `VSA/src` on this branch with the old FlowDroid jar (`-PflowdroidJar=libs/soot-infoflow-cmd-jar-with-dependencies.jar -PjavaRelease=11`) | 4.4.1 |
| **upgraded** | built from `VSA/src` on this branch (default build) + rebuilt `InstrumentationAgent.jar` | 4.7.1 (FlowDroid 2.15.1) |

## Source used

`VSA/src` on `main` (commit `cb7ca5f`, "cleaned up code") is **not** what `vsa.jar` was built from. A bytecode comparison (`javap -c -p`, all 74 IoTScope classes, constant-pool indices and line numbers ignored) showed that the jar matches the **first commit, `8609458`** (2023-09-09). The only differences were compiler output (newer javac adds `String.valueOf` to string concatenation), a typo in a log message, a test `main()` and an equivalent refactoring of the output path. The resources also match, except `log4j2.xml`, which was taken from the jar. This branch therefore restores `8609458`'s source. The later commits also change behaviour (CoAP simulation, URI handling, renamed classes) and were never used in a run.

The same comparison for the instrumentation agent found one branch missing from its source (`Map` fields are skipped in `toString()`); it was restored.

## Changes for Soot 4.7.1

| Change | Why |
|---|---|
| `Body.getParameterRefs()` → helper with the same logic in `BackwardContext` | removed from Soot |
| `ProcessManifest` no longer throws `XmlPullParserException` | FlowDroid API |
| `set_process_multiple_dex` removed | always on in Soot 4.7 |
| `ParameterTransferStmt` implements `get/setContainingBody`, `get*Unsafe`, `getOrComputeTag` | new interface methods |
| **Instrumentation agent skips `com.android.tools.smali.`** | Soot 4.7 renamed `org.jf.dexlib2`. The agent instrumented the renamed package; its generated `toString()` recursed until `StackOverflowError`. `CallGraph` swallowed the error, and **every analysis silently found nothing** (in 3 s). Now logged with the exception |
| `ValuePoint.solve()` catches `LinkageError` | source version of `patches/vsa-linkage-errors` |
| Not needed any more | `patches/arsc-typescount`, `patches/allow-cg-errors` (fixed in FlowDroid 2.15.1 / Soot 4.7.1) |
| Docker | `eclipse-temurin:17-jre` instead of 11 |

## Setup

`eclipse-temurin:17-jre` for all three jars, pass-1 settings of `execute_vsa.sh` (with the agent, `-Xmx12g`, Parallel GC, same log options, `config/exclude.json`). One JVM at a time; peak RSS from `/proc/<pid>/status` (VmHWM). Apps: `com.rainbow.drone` 5.15, `com.coolkit` (eWeLink) 5.x.

## Results

Value points are matched by method + target signature (the Jimple statement text differs between Soot versions because locals are named differently); values are compared as sets, with `Object@hash` normalised.

**orig vs baseline** (is the source right?)

| | drone | eWeLink |
|---|---|---|
| crypto, mqtt, udp, webview | identical | identical |
| endpoints | identical (42 value points, 115 values) | same 53 value points; 4 values only in orig, 12 only in baseline |

eWeLink endpoints is not deterministic: today's orig run and the production result of the **same jar** differ by 31/7 values. The baseline is therefore equivalent to the jar.

**orig vs upgraded**

| | drone | eWeLink |
|---|---|---|
| crypto | identical | identical |
| mqtt | identical (0) | identical (0) |
| udp | identical | 26 value points both; **+7 values**, −1 (new: multicast `239.46.0.0`/`239.48.0.0`, broadcast `255.255.255.255`, bind on port `65123`, NTP `time.android.com`) |
| webview | identical | 3 values fewer (all the bare fragment `https://` in JPush) |
| endpoints | 42 value points both; 113 of 115 values (2 URL fragments missing) | 53 value points both; 8 only in orig, 9 only in upgraded (within run-to-run variation) |

**Resources and errors** (seconds / peak MB / `Failed Typing` lines per run)

| | orig | baseline | upgraded |
|---|---|---|---|
| drone, 5 analyses | 228 s, ≤ 8.1 GB, 0 | 228 s, ≤ 8.1 GB, 0 | 295 s, ≤ 8.3 GB, 1 |
| eWeLink, 5 analyses | 654 s, ≤ 13.0 GB, 2 | 613 s, ≤ 12.9 GB, 2 | 731 s, ≤ 13.0 GB, 3 |

- **Run time:** about 10–25 % longer with Soot 4.7.1, mostly start-up (loading classes and building bodies); the solve times in the result files are about the same.
- **Memory:** the same.
- **`Failed Typing`:** a few per app in both versions, in **different** methods, all library code (old: an obfuscated `u8.k$d`/`u8.l$d`; new: JPush `ComponentInfo a(...)` ×3, DJI's bundled RxJava). Soot 4.7's typing does not fail less on these apps; it fails elsewhere.

## Assessment

- The upgraded VSA gives equivalent results on both apps (one analysis slightly better, one slightly worse in uninformative fragments) and runs on a maintained Soot/FlowDroid without the bytecode patches.
- On these small apps it brings **no memory or typing advantage**. Whether it helps on Tapo and Smart Life (which ran out of memory at 44 GB in crypto, mqtt and udp) has not been tested: that needs the 64 GB machine. Suggested test: Tapo crypto with the upgraded image, same settings as the laptop run.
