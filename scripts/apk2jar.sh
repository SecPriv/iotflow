#!/bin/bash
# Converts an APK to the jar IoTFlow uses for reflection-based simulation, one DEX file at a time.
#
# Why: dex2jar 2.4.38 fails on some large multi-DEX APKs when given the whole APK
# (e.g. com.tplink.iot, 18 DEX files: OutOfMemoryError after a few seconds even with a 16 GB heap),
# although every DEX file converts fine on its own. On failure the VSA keeps a 22-byte
# placeholder jar and never retries, so the simulation silently loses all app classes.
#
# The VSA and FlowAnalysis skip their own conversion when <name>-dex2jar.jar already exists,
# so run this before starting the containers:
#   scripts/apk2jar.sh VSA/docker/apps_to_analyze/<app>.apk
# The jar is written to VSA/docker/apps_to_analyze/jarFiles/ and copied to FlowAnalysis.
set -euo pipefail

APK=$(realpath "$1")
ROOT=$(cd "$(dirname "$0")/.." && pwd)
D2J="$ROOT/dependencies/dex_tools_2.4.38/d2j-dex2jar.sh"
NAME=$(basename "$APK" .apk)
OUT="$ROOT/VSA/docker/apps_to_analyze/jarFiles/$NAME-dex2jar.jar"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

unzip -q "$APK" 'classes*.dex' -d "$TMP/dex"
mkdir -p "$TMP/jars"
for dex in "$TMP"/dex/classes*.dex; do
    n=$(basename "$dex" .dex)
    D2J_XMX=${D2J_XMX:-6g} sh "$D2J" -f -o "$TMP/jars/$n.jar" "$dex" > "$TMP/jars/$n.log" 2>&1 || true
    size=$(stat -c%s "$TMP/jars/$n.jar" 2>/dev/null || echo 0)
    if [ "$size" -lt 1000 ]; then
        echo "FAILED: $n ($(grep -m1 -aoE '(OutOfMemory|Exception)[^	]{0,100}' "$TMP/jars/$n.log"))" >&2
        exit 1
    fi
    echo "$n: $size bytes"
done

# Merge; a class present in several DEX files keeps the first copy (classes.dex, classes2.dex, ...)
python3 -I - "$OUT.tmp" "$TMP"/jars/classes.jar $(ls "$TMP"/jars/classes[0-9]*.jar 2>/dev/null | sort -V) <<'EOF'
import sys, zipfile
out, jars = sys.argv[1], sys.argv[2:]
seen, dup = set(), 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for j in jars:
        with zipfile.ZipFile(j) as src:
            for e in src.infolist():
                if e.is_dir():
                    continue
                if e.filename in seen:
                    dup += 1
                    continue
                seen.add(e.filename)
                z.writestr(e.filename, src.read(e))
print(f"merged {len(jars)} jars: {len(seen)} entries, {dup} duplicates skipped")
EOF
mkdir -p "$(dirname "$OUT")"
mv "$OUT.tmp" "$OUT"
FA="$ROOT/FlowAnalysis/docker/apps_to_analyze/jarFiles"
mkdir -p "$FA" && cp -f "$OUT" "$FA/"
echo "wrote $OUT (and copied to FlowAnalysis)"
