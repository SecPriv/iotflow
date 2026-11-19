#!/bin/bash
# Runs the VSA, then the flow analysis, on everything in */docker/apps_to_analyze/, detached from
# any terminal: closing the terminal or Claude Code session doesn't stop it.
#
#   setsid nohup scripts/run_pipeline.sh > /dev/null 2>&1 &
#
# Convert the apps first with scripts/apk2jar.sh. If a stage's container is already running, the
# script attaches to it instead of starting it again. Progress: apps/pipeline.log; filtered logs:
# apps/vsa_run.log and apps/dfa_run.log (the noisiest warnings are dropped). Full container logs:
# docker logs <container> (capped by compose.yaml).
R=$(cd "$(dirname "$0")/.." && pwd)
LOGDIR=$R/apps
FILTER='SimulateEngine|BackwardStmtSwitch'
mkdir -p "$LOGDIR"

d() {  # docker, via sg if this shell doesn't have the docker group yet
    if id -nG | grep -qw docker; then docker "$@"; else sg docker -c "docker $(printf '%q ' "$@")"; fi
}
note() { echo "$(date '+%F %T') $*" >> "$LOGDIR/pipeline.log"; }

stage() {  # $1 = VSA|FlowAnalysis, $2 = compose service, $3 = log file
    cd "$R/$1/docker" || return 1
    cid=$(d compose ps -q --status running "$2")
    if [ -n "$cid" ]; then
        note "$1: attaching to running container"
        since=(--since "$(date -Iseconds)")
    else
        note "$1: starting"
        d compose up --build -d >> "$LOGDIR/pipeline.log" 2>&1 || { note "$1: compose up failed"; return 1; }
        cid=$(d compose ps -q "$2")
        since=()
    fi
    d logs -f "${since[@]}" "$cid" 2>&1 | grep --line-buffered -avE "$FILTER" >> "$LOGDIR/$3" &
    code=$(d wait "$cid")
    wait
    note "$1: finished, exit code $code"
}

note "pipeline started"
stage VSA vsa_docker vsa_run.log
# The flow analysis reuses the VSA's jars (normally already copied there by apk2jar.sh)
for j in "$R"/VSA/docker/apps_to_analyze/jarFiles/*.jar; do
    t="$R/FlowAnalysis/docker/apps_to_analyze/jarFiles/$(basename "$j")"
    [ -s "$t" ] && [ "$(stat -c%s "$t")" -gt 1000 ] || cp -f "$j" "$t"
done
stage FlowAnalysis dfa_docker dfa_run.log
note "pipeline done"
