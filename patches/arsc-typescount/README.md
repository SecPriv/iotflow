# Patch: FlowDroid ARSC parser and `ResTable_typeSpec.typesCount`

## Problem

All bundled analysis jars contain FlowDroid `soot-infoflow-android` 2.12.0-SNAPSHOT (early 2023). Its resource table parser (`soot.jimple.infoflow.android.resources.ARSCFileParser`) rejects apps built with recent Android build tools:

```
java.lang.RuntimeException: File format violation, res1 was not zero
    at soot.jimple.infoflow.android.resources.ARSCFileParser.readTypeSpecTable(...)
```

In recent Android versions, the former reserved field `res1` of `ResTable_typeSpec` holds `typesCount`, so it is non-zero. Every analysis of such an app stops at start-up. Example: `com.rainbow.drone` 5.15, target SDK 35.

## Fix

`PatchArsc.java` edits the compiled class with ASM. It removes only this one check in `readTypeSpecTable`:
- The field is still read and stored.
- All other format checks are unchanged, including `ResTable_type.res0`, which holds flags such as "sparse" that the old parser cannot handle. Those cases still fail loudly instead of being misread.

Patched jars:

| Jar | Parser class version |
|---|---|
| `VSA/docker/vsa.jar` | A |
| `FlowAnalysis/docker/dependencies/vsa.jar` | A |
| `VSA/libs/soot-infoflow-cmd-jar-with-dependencies.jar` | A (used when building VSA from source) |
| `FlowAnalysis/docker/iotflow.jar` | B |
| `FlowAnalysis/libs/soot-infoflow-new-build.jar` | B (used when building FlowAnalysis from source) |

Verification on `com.rainbow.drone` 5.15:
- **Original class:** throws the error above.
- **Patched class:** parses 1 package, 19 types and 38,043 resources.
- **Resolved values are correct:** the manifest label `@7F12006E` resolves to `app_name_rainbow = "Rainbow"`, which matches the store listing.

## Re-applying

```bash
P=soot/jimple/infoflow/android/resources/ARSCFileParser.class
CP=VSA/docker/vsa.jar            # any jar containing ASM (org.objectweb.asm)
javac -cp $CP -d /tmp/patch patches/arsc-typescount/PatchArsc.java
unzip -o <jar> $P -d /tmp/orig
java -cp $CP:/tmp/patch PatchArsc /tmp/orig/$P /tmp/out/$P   # create /tmp/out/<dir of $P> first
(cd /tmp/out && zip -q <absolute path of jar> $P)
```

The patcher refuses to write anything if the bytecode around the check is not exactly as expected.

## Note

androguard 3.3.5, pinned in `FlowAnalysis/docker/scripts/requirements.txt`, has the same bug ("res1 must be zero!"). IoTFlow only uses androguard for permissions and class names, which still work. Any androguard call that reads resources (e.g. `get_app_name()`) fails on such apps.
