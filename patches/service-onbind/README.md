# Fix: FlowDroid 2.15 aborts on services without their own `onBind()`

Unlike the other folders in `patches/`, this is a **source change**: a fixed copy of FlowDroid's class in [`FlowAnalysis/src/main/java/soot/jimple/infoflow/android/entryPointCreators/components/ServiceEntryPointCreator.java`](../../FlowAnalysis/src/main/java/soot/jimple/infoflow/android/entryPointCreators/components/ServiceEntryPointCreator.java), which replaces FlowDroid's own when `iotflow.jar` is built (like IoTFlow's other replacement classes).

## Problem

Every FlowDroid run on WiZ (`com.wizconnected.wiz2` 1.38.6) aborted while building the entry point, 2026-11-19:

```
The data flow analysis has failed. Error message: cannot set body for non-concrete method!
    <android.app.Service: android.os.IBinder onBind(android.content.Intent)>
  at soot.SootMethod.setActiveBody(SootMethod.java:391)
  at soot.jimple.infoflow.android.entryPointCreators.components.ServiceEntryPointCreator.instrumentOnBind(ServiceEntryPointCreator.java:204)
```

- FlowDroid instruments every service's `onBind()` to store the returned binder. FlowDroid 2.15 looks the method up with `SootUtils.findMethod()`, which also searches **superclasses**; FlowDroid 2.12 only looked in the service class itself (`getMethodUnsafe`).
- If a service does not implement `onBind()` and its superclasses do not either, the lookup ends at the **abstract** `android.app.Service.onBind()`. FlowDroid then tries to give that abstract framework method a body, which Soot refuses, and the whole run aborts.
- In WiZ: `com.wizconnected.wiz2.app_controls.DeviceControlService` extends `android.service.controls.ControlsProviderService`. The APK bundles its own **empty stub** of that framework class (only a static initialiser, extends `android.app.Service` directly), probably a compile-time stub packaged by mistake. On a phone, Android's real class is used; FlowDroid sees the stub.
- The same code is in FlowDroid's current `develop` branch, so this is not fixed upstream.

## Fix

In `instrumentOnBind()`: if the `onBind()` found is not concrete and declared in **another** class, create a new `onBind()` in the service class itself (the FlowDroid 2.12 behaviour), instead of adding a body to the inherited abstract method. If the service declares an abstract `onBind()` itself, `ABSTRACT` is removed before the body is added. Services with a concrete `onBind()` (own or inherited) are handled exactly as before.

## Verification

WiZ, `config/general.xml`, 12 GB, 120 s callback and data-flow timeouts, 2026-11-19:

| | FlowDroid 2.15.1 | with this fix |
|---|---|---|
| Result | aborts after 2 s with the error above | completes (`DataFlowOutOfMemory` at 12 GB, i.e. partial) |
| Run time | – | 439 s (call graph 186 s) |
| Flows | – | 56 |

Apps that ran before are unaffected as long as their services have a concrete `onBind()` somewhere in the hierarchy (otherwise they would have aborted too). One case does change: if the `onBind()` found is in a *phantom* superclass, 2.15.1 gave that superclass's method a body; now the method is created in the service itself, which models the same behaviour.

## Rebuilding

See [FlowAnalysis/README.md](../../FlowAnalysis/README.md) ("Building"), then copy `build/libs/iotflow.jar` to `FlowAnalysis/docker/`.
