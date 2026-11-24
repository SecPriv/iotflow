# Patch: IoTScope (VSA) skips backward paths that hit a `LinkageError`

> **Since 2026-11-19 there is only one copy of `vsa.jar`:** `dependencies/vsa.jar` (shared by both stages). The jar paths below are the ones at the time of patching.

## Problem

WiZ (`com.wizconnected.wiz2` 1.38.6), endpoints analysis, 2026-11-19:

```
Exception in thread "main" java.lang.VerifyError: Expecting a stackmap frame at branch target 43
  Location: kotlin/jvm/internal/x.<clinit>()V @2: ldc
    at kotlin.jvm.internal.m.toString(Unknown Source)
    at java.lang.String.format(...)
    ...
    at soot.jimple.internal.JAssignStmt.apply(JAssignStmt.java:217)
    at iotscope.graph.ValuePoint.solve(ValuePoint.java:158)
    at iotscope.graph.DataDependenceGraph.solve(DataDependenceGraph.java:53)
    at iotscope.main.Main.getAllSolvedValuePoints(Main.java:110)
```

- The simulation (`SimulateEngine`) builds debug messages with `String.format(..., value)` even at log level `warn`. That calls `toString()` on a simulated object of the app (here `kotlin.jvm.internal.m`), which loads another app class from the dex2jar jar.
- dex2jar did not emit the stackmap frames Java's verifier requires for that class, so loading it throws `VerifyError`.
- Nothing between `ValuePoint.solve()` and `main` catches it: the analysis of the whole app ended. The JVM kept running until the 40-minute timeout, because other threads were still alive.

## Fix

`PatchValuePointSolve.java` (ASM) wraps `tmp.simulate(); mergeResult(bc, tmp);` in `ValuePoint.solve()` with `try { ... } catch (LinkageError e) { /* skip this backward context */ }`.
- `LinkageError` covers `VerifyError`, `NoClassDefFoundError`, `ExceptionInInitializerError`, `ClassFormatError`.
- Only the affected backward path of one value point is lost. Other errors, e.g. `OutOfMemoryError`, still propagate.
- The patched class passes `-Xverify:all` on Java 11.

Patched jars (identical class before and after): `VSA/docker/vsa.jar`, `FlowAnalysis/docker/dependencies/vsa.jar`.

The jar was built from a slightly different source than `VSA/src` (line numbers differ), so the fix is applied to the bytecode, not the source.

## Rejected alternative: turning off verification

Running the VSA with `-XX:+UnlockDiagnosticVMOptions -XX:-BytecodeVerificationRemote` makes the class load (tested), but then the JVM executes the faulty bytecode: all three passes of the WiZ endpoints analysis crashed with `SIGSEGV` in `libjvm.so` (`SATBMarkQueue::filter`, `LinkResolver::resolve_invoke`). The flag was removed again.

## Re-applying

```bash
P=iotscope/graph/ValuePoint.class
J=dependencies/vsa.jar
javac -cp $J -d /tmp/patch patches/vsa-linkage-errors/PatchValuePointSolve.java
mkdir -p /tmp/orig /tmp/out/iotscope/graph && unzip -o $J $P -d /tmp/orig
java -cp $J:/tmp/patch PatchValuePointSolve $J /tmp/orig/$P /tmp/out/$P
(cd /tmp/out && zip <absolute path of each vsa.jar> $P)
```
