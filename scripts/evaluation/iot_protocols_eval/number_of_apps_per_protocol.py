import json

PROTOCOL = 'xmpp'

DATASETS = ['iotprofiler', 'iotspotter', 'neupane']

mqtt_apps = set()

#ENDPOINTS = json.load(open('mqtt_total.json'))
#ENDPOINTS = open('local_endpoints_mqtt.txt').readlines()
ENDPOINTS = json.load(open('xmpp_data/unique_endpoints.json'))
#ENDPOINTS = json.load(open('amqp_data/endpoints.json'))
#ENDPOINTS = json.load(open('coap_data/endpoints.json'))
#ENDPOINTS_2 = json.load(open('mqtt_data/aws_endpoints.json'))

#print(ENDPOINTS_2)

def check_mqtt_endpoints_local(v):
    for e in ENDPOINTS:
        if e.strip('\n') in v or 'fromUI.local' == v:
            return True
    return False

def check_mqtt_endpoints(v):
    for k,val in ENDPOINTS.items():
        if k in v:
            return True
    for e2 in ENDPOINTS_2:
        if e2 in v:
            return True
    return False

def check_xmpp_endpoints(v):
    for e in ENDPOINTS:
        if e in v:
            return True
    return False

def check_coap_local(v):
    for e in ENDPOINTS:
        if e in v or 'fromUI.local' in v:
            return True
    return False

for d in DATASETS:
    reconstructed_values = json.load(open(d + '_' + PROTOCOL + '.json'))
    for app in reconstructed_values:
        for val in app['reconstructed_values']:
            #if 'coaps://' in val and 'fromUI.local' not in val: #'fromUI.local' == val:
            if 'fromUI.local' == val:
                mqtt_apps.add(app['app_name'])
            # if check_xmpp_endpoints(val):
            #     mqtt_apps.add(app['app_name'])
            # if check_mqtt_endpoints(val):
            #     mqtt_apps.add(app['app_name'])

print(mqtt_apps)
print(len(mqtt_apps))