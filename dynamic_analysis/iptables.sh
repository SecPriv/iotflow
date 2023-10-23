# MITM_INTERFACE: network interface to MITM
MITM_INTERFACE="wlp0s20f3"
# MITM_PORTS: TCP ports to MITM (HTTP and HTTPS). Please use commas to separate them.
MITM_PORTS="1:65535"
# MITM_LISTENING_PORT: TCP listening port used by mitmdump
MITM_LISTENING_PORT="8080"

iptables -t nat -N MITM -w 2 &> /dev/null
iptables -t nat -F MITM -w 2
sleep 2

iptables -t nat -A PREROUTING -j MITM -w 2
sleep 2

iptables -t nat -A MITM -i $MITM_INTERFACE -p tcp -m tcp -m multiport --dports $MITM_PORTS -j REDIRECT --to-ports $MITM_LISTENING_PORT -w 2
#iptables -t nat -A MITM -i $MITM_INTERFACE -p udp -m udp -m multiport --dports $MITM_PORTS -j REDIRECT --to-ports $MITM_LISTENING_PORT -w 2
#iptables -A INPUT -i $MITM_INTERFACE -p udp -m udp -m multiport --dports 1:52,54:65535 -j DROP
#iptables -t nat -A MITM -i wlp0s20f3 -p tcp -m tcp -m multiport --dports 1:65535 -j REDIRECT --to-ports 8080
#iptables -t nat -A MITM -i wlp0s20f3 -p tcp -m udp -m multiport --dports 1:65535 -j REDIRECT --to-ports 8080
