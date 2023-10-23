import socket
import json

DATASET = 'iotspotter'
PROTOCOL = 'xmpp'

file = '../verified_iot_datasets/filtered_endpoints/' + DATASET + '_endpoints_' + PROTOCOL + '.json'

domains_datasets = json.load(open(file, 'r'))

def notResolving(hostname):
    try:
        return socket.gethostbyname(hostname) == None
    except UnicodeError as e:
        return True
    except socket.gaierror as e:
        return True

for domain in domains_datasets:
    if notResolving(domain):
        print(domain)