#!/bin/sh
# Runs the value set analysis for one app ($1).
# Analyses: endpoints, crypto, mqtt, udp, webview (override with the ANALYSES environment variable).
# Configs live in /vsa/config/<name>.json.
#
# Each analysis runs up to three passes until one produces a result:
#   1. with the instrumentation agent (less memory, fewer duplicates)
#   2. without the agent; skipped if pass 1 hit the time limit (pass 2 is not faster, only
#      different when the agent itself causes a problem)
#   3. without the agent and less precise (-mb 20 -mbc 100)
# mb = backward steps, mbc = backward paths, tb = timeout backward tracing, tf = timeout forward computation
#
# Markers in /results/<analysis>/ (later runs skip the analysis; delete the marker to retry):
#   <package>.error    fatal error: an uncaught exception in the main thread, a JVM crash or an
#                      OutOfMemoryError (with the Parallel GC this includes "GC overhead limit exceeded"
#                      when the heap is too small). The analysis is stopped 5 s after the error line
#                      instead of waiting for the time limit; the file holds the error and stack trace.
#   <package>.timeout  the last pass also hit the time limit (VSA_TIMEOUT)
# scripts/run_pipeline.sh passes both to the flow stage, which then skips the same IoTScope analysis.
#
# Several apps can run at the same time (see run.sh): the stop only kills this app's own JVM.

echo "Analysing: $1"

# amqp, coap, mqtt, xmpp, udp and endpoints are also run by the FlowAnalysis stage, so coap/amqp/xmpp are
# not repeated here. webview is run by neither stage otherwise.
ANALYSES="${ANALYSES:-endpoints crypto mqtt udp webview}"
# Time limit per analysis pass (timeout(1) syntax, e.g. 40m, 2h); after it, Java gets 5 more minutes to stop
# (a stopped pass writes its partial result within seconds; on the laptop, Smart Life passes that hit the
# limit never stopped by themselves and used the former 50-minute grace period every time)
VSA_TIMEOUT="${VSA_TIMEOUT:-40m}"
# Heap and exclusion list can be overridden for large apps (VSA_XMX, VSA_EXCLUDE; see compose.yaml)
# Do not turn off bytecode verification (-XX:-BytecodeVerificationRemote): with it, faulty dex2jar classes
# crashed the JVM (SIGSEGV). VerifyErrors are handled in the VSA instead (patches/vsa-linkage-errors).
# Logging: warn level; the simulation (iotscope.forwardexec), backward slicing and resource lookups are
# switched off: they produced >99 % of all lines (millions per hour) and do not change the results.
# Kept: iotscope.main, Soot's "Failed Typing" errors, all fatal errors.
LOG_OPTS="-Dorg.slf4j.simpleLogger.defaultLogLevel=warn -Dorg.slf4j.simpleLogger.log.iotscope.forwardexec=off -Dorg.slf4j.simpleLogger.log.iotscope.backwardslicing=off -Dorg.slf4j.simpleLogger.log.iotscope.main.ApkContext=off"
JAVA_OPTS="-Xms5g -Xmx${VSA_XMX:-16g} -XX:+UseParallelGC $LOG_OPTS"
VSA_ARGS="-p /vsa/dependencies/android-31.jar -t /vsa/config/taintrules.json -e ${VSA_EXCLUDE:-/vsa/config/exclude.json} -dj /vsa/dependencies/dex_tools_2.4.38/d2j-dex2jar.sh --dont_overwrite"

APK="$1"
PKG=$(basename "$APK" .apk)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Runs one pass. $1 = analysis, $2 = pass number, $3 = extra JVM options, $4 = extra VSA options.
# Afterwards $TMP/$1.timedout exists if this pass hit the time limit.
run() {
    config=$1
    [ "$config" = "crypto" ] && config=javaCrypto
    base="/results/$1/$PKG"
    rm -f "$TMP/$1.timedout"
    # an empty json is not a result: the VSA creates the file before writing it, so a pass stopped at the
    # time limit can leave a 0-byte file (Tapo mqtt on the laptop, 2026-11-23)
    [ -e "$base.json" ] && [ ! -s "$base.json" ] && rm -f "$base.json"
    [ -s "$base.json" ] && return
    for m in error timeout; do
        if [ -e "$base.$m" ]; then
            echo "[$PKG/$1] skipped: an earlier run stopped ($base.$m)"
            return
        fi
    done
    mkdir -p "/results/$1"
    echo "[$PKG/$1] pass $2"
    # sh -c writes its PID and then becomes timeout(1), whose child is the JVM: the guard kills exactly that JVM
    { sh -c 'echo $$ > "$0"; exec "$@"' "$TMP/$1.pid" \
        timeout --foreground --kill-after=5m "$VSA_TIMEOUT" \
        java $3 $JAVA_OPTS -jar /vsa/dependencies/vsa.jar -d /vsa/config/$config.json -o /results/$1/ -a "$APK" $VSA_ARGS $4
      echo $? > "$TMP/$1.status"; } 2>&1 \
      | awk -W interactive -v marker="$base.error" -v pidfile="$TMP/$1.pid" -v tag="[$PKG/$1] " '
          # -W interactive: mawk otherwise reads pipes in large blocks and would not see the error line while the JVM hangs
          # every line is tagged with app and analysis, because several apps can run at the same time
          { print tag $0; fflush() }
          # keep the error line and the stack trace after it (up to 40 lines) in the marker file
          stopped && kept < 40 { print > marker; kept++ }
          !stopped && /Exception in thread "main"|A fatal error has been detected by the Java Runtime|java\.lang\.OutOfMemoryError/ {
              stopped = 1
              print > marker
              print tag "[execute_vsa] fatal error, stopping this analysis in 5 s: " $0; fflush()
              # delayed, so the stack trace still reaches the log; kills only the JVM of this pass
              # (the child of timeout(1)) and its own children (e.g. a dex2jar run started by the VSA)
              getline pid < pidfile
              system("(sleep 5; for j in $(pgrep -P " pid " -x java); do pkill -KILL -P $j; kill -KILL $j; done) &")
          }
          END { if (stopped) close(marker) }'
    status=$(cat "$TMP/$1.status" 2>/dev/null)
    [ -e "$base.json" ] && [ ! -s "$base.json" ] && rm -f "$base.json"
    # 124: time limit reached; 137: killed after the grace period (also the code after a guard stop, hence the marker check)
    if [ "$status" = 124 ] || { [ "$status" = 137 ] && [ ! -e "$base.error" ]; }; then
        echo "[$PKG/$1] pass $2 hit the time limit ($VSA_TIMEOUT)"
        touch "$TMP/$1.timedout"
    fi
}

for a in $ANALYSES; do
    run "$a" 1 "-javaagent:/vsa/dependencies/InstrumentationAgent.jar" ""
    if [ -e "$TMP/$a.timedout" ]; then
        echo "[$PKG/$a] pass 2 skipped (pass 1 hit the time limit)"
    else
        run "$a" 2 "" ""
    fi
    run "$a" 3 "" "-mb 20 -mbc 100"
    # (the VSA often still writes a partial result when stopped at the time limit; then no marker)
    if [ -e "$TMP/$a.timedout" ] && [ ! -s "/results/$a/$PKG.json" ]; then
        echo "all passes that ran hit the time limit (VSA_TIMEOUT=$VSA_TIMEOUT), $(date -u '+%F %T') UTC" > "/results/$a/$PKG.timeout"
    fi
done
