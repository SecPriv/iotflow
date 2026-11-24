#!/bin/bash
# Switches the VSA (dependencies/vsa.jar + InstrumentationAgent.jar, used by both stages) between
#   4.4  the VSA used so far (FlowDroid 2.12 / Soot 4.4.1, with the bytecode patches in patches/)
#   4.7  the port to FlowDroid 2.15.1 / Soot 4.7.1 (branch vsa-soot-upgrade,
#        patches/VALIDATION-vsa-soot-4.7.md on that branch)
#
#   scripts/vsa_version.sh status|4.4|4.7
#
# The jars of each version are kept in dependencies/vsa-soot-4.4/ and dependencies/vsa-soot-4.7/
# (the 4.4 copy is made the first time you switch away from it). Do not switch while an analysis runs.
set -e
D=$(cd "$(dirname "$0")/.." && pwd)/dependencies

current() {
    for v in 4.4 4.7; do
        if [ -e "$D/vsa-soot-$v/vsa.jar" ] && cmp -s "$D/vsa.jar" "$D/vsa-soot-$v/vsa.jar"; then echo "$v"; return; fi
    done
    if [ ! -e "$D/vsa-soot-4.4/vsa.jar" ]; then echo "4.4 (not switched yet)"; else echo "unknown (dependencies/vsa.jar matches neither copy)"; fi
}

case "$1" in
    status|"")
        echo "VSA in use: Soot $(current)" ;;
    4.4|4.7)
        if [ ! -e "$D/vsa-soot-4.4/vsa.jar" ]; then
            [ "$1" = 4.7 ] || { echo "no saved copy of the 4.4 VSA"; exit 1; }
            mkdir -p "$D/vsa-soot-4.4"
            cp -p "$D/vsa.jar" "$D/InstrumentationAgent.jar" "$D/vsa-soot-4.4/"
            echo "saved the current VSA to dependencies/vsa-soot-4.4/"
        fi
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -qE '^iotflow-(vsa|dfa)-'; then
            echo "an analysis container is running (docker ps); switch after it has finished"; exit 1
        fi
        cp "$D/vsa-soot-$1/vsa.jar" "$D/vsa-soot-$1/InstrumentationAgent.jar" "$D/"
        echo "VSA in use: Soot $(current)" ;;
    *)
        echo "usage: $0 status|4.4|4.7"; exit 1 ;;
esac
