#!/bin/bash
# Value set analysis of every APK in /apps_to_analyze (split APKs excluded).
#
# Apps are split by the size of their converted jar (apps_to_analyze/jarFiles/<package>-dex2jar.jar):
#   small (< VSA_SMALL_MB, default 100 MB): up to VSA_PARALLEL apps at the same time (default 1), each
#       with heap VSA_XMX_SMALL (default: VSA_XMX)
#   large (or no jar yet): afterwards, one at a time, with heap VSA_XMX
# Memory needed while small apps run: about VSA_PARALLEL x VSA_XMX_SMALL (+ about 1 GB per JVM).
# Example for 64 GB: VSA_PARALLEL=3 VSA_XMX_SMALL=16g VSA_XMX=44g
PARALLEL=${VSA_PARALLEL:-1}
SMALL_MB=${VSA_SMALL_MB:-100}
XMX_SMALL=${VSA_XMX_SMALL:-${VSA_XMX:-16g}}

small=()
large=()
for apk in /apps_to_analyze/*.apk; do
    [ -e "$apk" ] || continue
    case "$apk" in *.split.*) continue ;; esac
    jar="/apps_to_analyze/jarFiles/$(basename "$apk" .apk)-dex2jar.jar"
    if [ -s "$jar" ] && [ "$(stat -c%s "$jar")" -lt $((SMALL_MB * 1024 * 1024)) ]; then
        small+=("$apk")
    else
        large+=("$apk")
    fi
done
echo "VSA: ${#small[@]} small app(s), up to $PARALLEL at a time with heap $XMX_SMALL; ${#large[@]} large app(s), one at a time with heap ${VSA_XMX:-16g}"

running=0
for apk in "${small[@]}"; do
    if [ "$running" -ge "$PARALLEL" ]; then
        wait -n
        running=$((running - 1))
    fi
    VSA_XMX=$XMX_SMALL /vsa/execute_vsa.sh "$apk" &
    running=$((running + 1))
done
wait

for apk in "${large[@]}"; do
    /vsa/execute_vsa.sh "$apk"
done
