echo "Analysing: $1";

#normal run
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar   -d /vsa/config/amqp.json  -p  /vsa/dependencies/android-31.jar -o /results/amqp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/coap.json  -p  /vsa/dependencies/android-31.jar -o /results/coap/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar   -d /vsa/config/mqtt.json  -p  /vsa/dependencies/android-31.jar -o /results/mqtt/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar   -d /vsa/config/endpoints.json  -p  /vsa/dependencies/android-31.jar -o /results/endpoints/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar   -d /vsa/config/xmpp.json  -p  /vsa/dependencies/android-31.jar -o /results/xmpp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/udp.json  -p  /vsa/dependencies/android-31.jar -o /results/udp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/javaCrypto.json  -p  /vsa/dependencies/android-31.jar -o /results/crypto/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -javaagent:/vsa/dependencies/InstrumentationAgent.jar -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/webview.json  -p  /vsa/dependencies/android-31.jar -o /results/webview/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;




#without agent
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/mqtt.json  -p  /vsa/dependencies/android-31.jar -o /results/mqtt/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/amqp.json  -p  /vsa/dependencies/android-31.jar -o /results/amqp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/coap.json  -p  /vsa/dependencies/android-31.jar -o /results/coap/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/endpoints.json  -p  /vsa/dependencies/android-31.jar -o /results/endpoints/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/xmpp.json  -p  /vsa/dependencies/android-31.jar -o /results/xmpp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/udp.json  -p  /vsa/dependencies/android-31.jar -o /results/udp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/javaCrypto.json  -p  /vsa/dependencies/android-31.jar -o /results/crypto/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/webview.json  -p  /vsa/dependencies/android-31.jar -o /results/webview/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite;



#without agent -- and less precise
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/mqtt.json  -p  /vsa/dependencies/android-31.jar -o /results/mqtt/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/amqp.json  -p  /vsa/dependencies/android-31.jar -o /results/amqp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/coap.json  -p  /vsa/dependencies/android-31.jar -o /results/coap/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/endpoints.json  -p  /vsa/dependencies/android-31.jar -o /results/endpoints/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar  -d /vsa/config/xmpp.json  -p  /vsa/dependencies/android-31.jar -o /results/xmpp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/udp.json  -p  /vsa/dependencies/android-31.jar -o /results/udp/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/javaCrypto.json  -p  /vsa/dependencies/android-31.jar -o /results/crypto/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite  -mb 20 -mbc 100;
timeout --foreground --kill-after=50m 40m java -Xms5g -Xmx16g -jar /vsa/vsa.jar -d /vsa/config/webview.json  -p  /vsa/dependencies/android-31.jar -o /results/webview/ -t /vsa/config/taintrules.json -a $1 -dj /vsa/dependencies/dex_tools_2.1/d2j-dex2jar.sh --dont_overwrite -mb 20 -mbc 100;



# mb = backward steps, mbc = backward paths, tb = timeout backward tracing, tf = timeout forward computation
