import time
import os

host_list = ["coap://coap.me","coap://224.0.1.187"]
port_list = [5683]

#java -cp lib/mjcoap.jar test.SimpleCoapClient GET coap://coap.me/sink
#java -cp lib/mjcoap.jar test.SimpleCoapClient PUT coap://coap.me/sink -b TEXT "test1234"


for i in range(len(host_list)):
    os.system("java -cp ./mjcoap-201018/lib/mjcoap.jar test.SimpleCoapClient GET " + host_list[i] + "/.well-known/core")