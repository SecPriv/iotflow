import paho.mqtt.client as mqtt
import time, json, socket, re

#0: Connection successful
#1: Connection refused – incorrect protocol version
#2: Connection refused – invalid client identifier
#3: Connection refused – server unavailable
#4: Connection refused – bad username or password
#5: Connection refused – not authorised

LOCAL_1 = "^127\."
LOCAL_2 = "^10\."
LOCAL_3 = "^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-1]\."
LOCAL_4 = "^192\.168\."

excluded = ['255.255.255.255', '0.0.0.0']

def check_if_local(e):
    if re.match(LOCAL_1, e) or re.match(LOCAL_2, e) or re.match(LOCAL_3, e) or re.match(LOCAL_4, e) or e in excluded:
        return True
    return False

DATASET = 'iotprofiler'

LOCAL_ENDPOINTS = set()

# mqtt_total.json is obtained by manually appending the results of filter_reconstructed_values_for_URLS.py into a single file
MQTT_TOTAL = json.load(open('../../verified_iot_datasets/mqtt_total.json', 'r'))


ANALYZED_ENDPOINTS = set()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code "+str(rc))
    else:
        print('Error code: ', str(rc))

def get_endpoint_and_port(e):
    if ':' in e:
        port_and_endpoint = e.split(':')
        return (port_and_endpoint[0], port_and_endpoint[1])
    return (e, 1883)

client = mqtt.Client(client_id='test')
client.on_connect = on_connect

for e, data in MQTT_TOTAL.items():

    (endpoint, port) = get_endpoint_and_port(e)

    if endpoint not in ANALYZED_ENDPOINTS:

        print("Analyzing", endpoint)
        try:
            client.connect(endpoint, port)

            client.loop_start()
            time.sleep(2)
            client.loop_stop()
            client.disconnect()
        except:
            print('Error connecting to', endpoint)

    print('\n')
    time.sleep(0.5)
