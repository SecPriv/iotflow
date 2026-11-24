#!/bin/bash
# Runs the VSA, then the flow analysis, on everything in */docker/apps_to_analyze/, detached from any
# terminal: closing the terminal or a Claude Code session does not stop it.
#
#   setsid nohup scripts/run_pipeline.sh > /dev/null 2>&1 &
#   VSA_PARALLEL=3 VSA_XMX_SMALL=16g VSA_XMX=44g MMF=30 MMI=12 setsid nohup scripts/run_pipeline.sh > /dev/null 2>&1 &   # 64 GB machine
#
# Put the base APKs into VSA/docker/apps_to_analyze/ and convert them with scripts/apk2jar.sh (the flow
# stage gets copies automatically). Settings are environment variables (see the Docker
# READMEs). If a stage's container is already running, the script attaches to it instead of starting it.
#
# Output: progress in apps/pipeline.log; logs in apps/vsa_run.log and apps/dfa_run.log (Docker keeps the
# full container logs: docker compose logs vsa|dfa). The containers run as the calling user, so all
# results belong to that user.
R=$(cd "$(dirname "$0")/.." && pwd)
LOGDIR=$R/apps
mkdir -p "$LOGDIR"
export HOST_UID=${HOST_UID:-$(id -u)} HOST_GID=${HOST_GID:-$(id -g)}

d() {  # docker, via sg if this shell doesn't have the docker group yet
    if id -nG | grep -qw docker; then docker "$@"; else sg docker -c "docker $(printf '%q ' "$@")"; fi
}
note() { echo "$(date '+%F %T') $*" >> "$LOGDIR/pipeline.log"; }

stage() {  # $1 = compose service (vsa|dfa), $2 = log file
    cd "$R" || return 1
    cid=$(d compose ps -q --status running "$1")
    if [ -n "$cid" ]; then
        note "$1: attaching to running container"
        since=(--since "$(date -Iseconds)")
    else
        note "$1: starting"
        if ! d compose up --build -d "$1" >> "$LOGDIR/build.log" 2>&1; then
            # The build needs Docker Hub (base image metadata) even when nothing changed; without internet
            # it fails. The scripts are mounted from the folder (compose.yaml), so an existing image is fine.
            img=$(d compose config --images "$1" 2>/dev/null | head -1)
            if [ -n "$img" ] && d image inspect "$img" > /dev/null 2>&1 \
                && d compose up --no-build -d "$1" >> "$LOGDIR/build.log" 2>&1; then
                note "$1: image build failed (no internet? see apps/build.log), using the existing image $img"
            else
                note "$1: could not start (see apps/build.log: build error, no internet without an existing image, or Docker Compose v1 instead of v2)"
                return 1
            fi
        fi
        cid=$(d compose ps -a -q "$1")
        since=()
    fi
    d logs -f "${since[@]}" "$cid" >> "$LOGDIR/$2" 2>&1 &
    code=$(d wait "$cid")
    wait
    note "$1: finished, exit code $code"
}

# The VSA stage already computes endpoints, mqtt and udp (and amqp/coap/xmpp if enabled) with the same
# configuration and jar as the flow stage; copy its results over so the flow stage skips them
reuse_vsa_results() {
    local n=0 s=0
    for a in endpoints mqtt udp amqp coap xmpp; do
        for f in "$R"/VSA/docker/results/$a/*.json; do
            [ -s "$f" ] || continue   # a 0-byte json is a pass stopped while writing, not a result
            pkg=$(basename "$f" .json)
            [ -e "$R/FlowAnalysis/docker/apps_to_analyze/$pkg.apk" ] || continue
            t="$R/FlowAnalysis/docker/results/$a/$pkg.json"
            if [ ! -s "$t" ]; then
                mkdir -p "$(dirname "$t")" && cp "$f" "$t" && n=$((n + 1))
            fi
        done
        # Analyses the VSA had to stop (fatal error / time limit): the flow stage's IoTScope, with less
        # memory, would only fail again, so it skips them when it finds <package>.vsa-error / .vsa-timeout
        for f in "$R"/VSA/docker/results/$a/*.error "$R"/VSA/docker/results/$a/*.timeout; do
            [ -e "$f" ] || continue
            pkg=$(basename "${f%.*}")
            [ -e "$R/FlowAnalysis/docker/apps_to_analyze/$pkg.apk" ] || continue
            [ -s "$R/FlowAnalysis/docker/results/$a/$pkg.json" ] && continue
            t="$R/FlowAnalysis/docker/results/$a/$pkg.vsa-${f##*.}"
            if [ ! -e "$t" ]; then
                mkdir -p "$(dirname "$t")" && cp "$f" "$t" && s=$((s + 1))
            fi
        done
    done
    note "reused $n VSA result(s) in the flow stage; ${s:-0} analysis/analyses the VSA had to stop will be skipped there"
}

# Both stages analyse the same apps: copy APKs and jars from the VSA input folder to the flow stage's
# input folder if they are missing there (so apps only need to be added to VSA/docker/apps_to_analyze/)
copy_inputs() {
    mkdir -p "$R/FlowAnalysis/docker/apps_to_analyze/jarFiles"
    for a in "$R"/VSA/docker/apps_to_analyze/*.apk; do
        [ -e "$a" ] || continue
        t="$R/FlowAnalysis/docker/apps_to_analyze/$(basename "$a")"
        [ -e "$t" ] || cp "$a" "$t"
    done
    for j in "$R"/VSA/docker/apps_to_analyze/jarFiles/*.jar; do
        [ -e "$j" ] || continue
        t="$R/FlowAnalysis/docker/apps_to_analyze/jarFiles/$(basename "$j")"
        [ -s "$t" ] && [ "$(stat -c%s "$t")" -gt 1000 ] || cp -f "$j" "$t"
    done
}

note "pipeline started (user $HOST_UID:$HOST_GID)"
if ! d compose version > /dev/null 2>&1; then
    note "stopped: 'docker compose' (Compose v2) is not available; see apps/build.log"
    d compose version >> "$LOGDIR/build.log" 2>&1
    exit 1
fi
copy_inputs
stage vsa vsa_run.log || { note "stopped: the VSA stage could not be started"; exit 1; }
copy_inputs
reuse_vsa_results
stage dfa dfa_run.log || { note "stopped: the flow stage could not be started"; exit 1; }
note "pipeline done"
