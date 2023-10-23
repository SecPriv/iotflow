# MITM_INTERFACE: network interface to MITM
MITM_INTERFACE="wlp0s20f3"
# MITM_PORTS: TCP ports to MITM (HTTP and HTTPS). Please use commas to separate them.
MITM_PORTS="1:65535"
# MITM_LISTENING_PORT: TCP listening port used by mitmdump
MITM_LISTENING_PORT="8080"

# Reset firewall rules
iptables -t nat -D MITM -i $MITM_INTERFACE -p tcp -m tcp -m multiport --dports $MITM_PORTS -j REDIRECT --to-ports $MITM_LISTENING_PORT -w 2
iptables -t nat -D MITM -i $MITM_INTERFACE -p udp -m udp -m multiport --dports $MITM_PORTS -j REDIRECT --to-ports $MITM_LISTENING_PORT -w 2

sleep 2

iptables -t nat -D PREROUTING -j MITM -w 2 &> /dev/null

sleep 2

iptables -t nat -F MITM -w 2 &> /dev/null
iptables -t nat -X MITM -w 2 &> /dev/null