# Patch: let Soot's call graph skip methods it cannot process

## Problem

FlowDroid runs on Shelly (`cloud.shelly.smartcontrol` 1.58.28) and WiZ (`com.wizconnected.wiz2` 1.38.6) aborted while building the call graph:

```
The data flow analysis has failed. Error message: An error occurred while processing <tx2: java.lang.Object invoke()> in callgraph
Caused by: java.lang.RuntimeException: Attempt to create VarNode of type boolean
    at soot.jimple.spark.pag.VarNode.<init>(VarNode.java:135)
    at soot.jimple.spark.pag.PAG.makeLocalVarNode(PAG.java:738)
    at soot.jimple.spark.builder.MethodNodeFactory.caseLocal(MethodNodeFactory.java:343)
    at soot.jimple.spark.builder.MethodNodeFactory.caseCastExpr(MethodNodeFactory.java:320)
    ...
    at soot.jimple.spark.solver.OnFlyCallGraph.processReachables(OnFlyCallGraph.java:116)
```

Cause, in Soot 4.4.1 (bundled with FlowDroid 2.12):
1. Soot's type inference for DEX code fails on some R8-optimised methods (the `Failed Typing ... Is not cast compatible: boolean <-- [0..127]` log lines). A local then keeps the type `boolean` although it is used as an object, e.g. `$r1 = (java.lang.Object) $z0`.
2. Spark (points-to analysis / call graph) refuses to create a pointer node of a primitive type. `OnFlyCallGraph.processReachables()` catches the error per method, but rethrows it unless `Options.v().allow_cg_errors()` is set, so one method aborts the whole FlowDroid run.

Affected methods seen so far: an obfuscated Kotlin lambda `tx2.invoke()`, `tj2.i(PreferenceGroup)` and `io.sentry.android.core.u0.<init>` (Shelly), `com.braze.ui.actions.UriAction.getIntentArrayWithConfiguredBackStack` (WiZ).

FlowDroid 2.15.1 / Soot 4.7.1 (reworked DEX typing) does not hit the error on the same APK. See the upgrade branch.

## Fix

`PatchCgErrors.java` edits the compiled `soot.jimple.spark.solver.OnFlyCallGraph` with ASM. It replaces the single call to `Options.allow_cg_errors()` in `processReachables()` with the constant `true`. Soot's own error path then applies: the error is logged (`[main] ERROR soot.jimple.spark.solver.OnFlyCallGraph - An error occurred while processing <method> in callgraph`) and the analysis continues.

**Cost:** the points-to graph has no information for the skipped method, so data flows that pass through exactly that method can be missed. Search the logs for `in callgraph` to list the skipped methods per app.

Patched jars (all contained the identical original class):

| Jar |
|---|
| `FlowAnalysis/docker/iotflow.jar` |
| `FlowAnalysis/libs/soot-infoflow-new-build.jar` |
| `FlowAnalysis/docker/dependencies/vsa.jar` |
| `VSA/docker/vsa.jar` |
| `VSA/libs/soot-infoflow-cmd-jar-with-dependencies.jar` |

Verification on Shelly (`-s config/general.xml`, 8 GB, data-flow timeout 120 s):
- **Original:** aborts after 24 s with the error above.
- **Patched:** skips `tx2.invoke()` and `tj2.i(...)`, completes (`TerminationState=DataFlowTimeout` because of the short test timeout) and reports 2 flows: Wi-Fi SSID → `SharedPreferences.putString`, Wi-Fi SSID → `Intent.putExtra`.

## Re-applying

```bash
P=soot/jimple/spark/solver/OnFlyCallGraph.class
CP=VSA/docker/vsa.jar            # any jar containing ASM (org.objectweb.asm)
javac -cp $CP -d /tmp/patch patches/allow-cg-errors/PatchCgErrors.java
mkdir -p /tmp/orig /tmp/out/$(dirname $P)
unzip -o FlowAnalysis/docker/iotflow.jar $P -d /tmp/orig
java -cp $CP:/tmp/patch PatchCgErrors /tmp/orig/$P /tmp/out/$P
(cd /tmp/out && zip <absolute path of the jar> $P)
```

## Related: `VerifyError` in IoTScope (VSA)

Separate problem, fixed with a JVM flag instead of a patch. IoTScope's simulation loads the dex2jar-converted app classes into the JVM; some lack the stackmap frames Java's verifier requires (`java.lang.VerifyError: Expecting a stackmap frame at branch target 43`, WiZ `kotlin.jvm.internal.x`). `VerifyError` is not caught by the simulation and killed the analysis. Both IoTScope call sites (`VSA/docker/execute_vsa.sh`, `FlowAnalysis/docker/scripts/iotflow.py`) now run with `-XX:+UnlockDiagnosticVMOptions -XX:-BytecodeVerificationRemote`. Verified: the WiZ class fails to load without the flags and loads with them (Java 11 and 17).
