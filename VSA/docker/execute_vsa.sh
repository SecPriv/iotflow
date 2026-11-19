#!/bin/sh
# Runs the value set analysis for one app ($1).
# Analyses: endpoints, crypto, mqtt, udp, webview (override with the ANALYSES environment variable).
# Configs live in /vsa/config/<name>.json.
#
# Each analysis runs up to three passes; --dont_overwrite makes a later pass skip any
# analysis that already produced a result:
#   1. with the instrumentation agent (less memory, fewer duplicates)
#   2. without the agent
#   3. without the agent and less precise (-mb 20 -mbc 100)
# mb = backward steps, mbc = backward paths, tb = timeout backward tracing, tf = timeout forward computation

echo "Analysing: $1"

# amqp, coap, mqtt, xmpp, udp and endpoints are also run by the FlowAnalysis stage, so coap/amqp/xmpp are
# not repeated here. webview is run by neither stage otherwise.
ANALYSES="${ANALYSES:-endpoints crypto mqtt udp webview}"
# Heap and exclusion list can be overridden for large apps (VSA_XMX, VSA_EXCLUDE; see compose.yaml)
# Bytecode verification off: the simulation loads dex2jar-converted app classes, some of which lack the
# stackmap frames Java requires (VerifyError, e.g. WiZ kotlin.jvm.internal.x), which aborted the analysis.
JAVA_OPTS="-Xms5g -Xmx${VSA_XMX:-16g} -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -XX:+UnlockDiagnosticVMOptions -XX:-BytecodeVerificationRemote"
VSA_ARGS="-p /vsa/dependencies/android-31.jar -t /vsa/config/taintrules.json -e ${VSA_EXCLUDE:-/vsa/config/exclude.json} -dj /vsa/dependencies/dex_tools_2.4.38/d2j-dex2jar.sh --dont_overwrite"

run() {  # $1 = analysis name, $2 = extra JVM options, $3 = extra VSA options
    config=$1
    [ "$config" = "crypto" ] && config=javaCrypto
    timeout --foreground --kill-after=50m 40m \
        java $2 $JAVA_OPTS -jar /vsa/vsa.jar -d /vsa/config/$config.json -o /results/$1/ -a "$APK" $VSA_ARGS $3
}

APK="$1"
for a in $ANALYSES; do run "$a" "-javaagent:/vsa/dependencies/InstrumentationAgent.jar" ""; done
for a in $ANALYSES; do run "$a" "" ""; done
for a in $ANALYSES; do run "$a" "" "-mb 20 -mbc 100"; done
