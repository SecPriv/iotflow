import whois
import socket
import json

base_path = '../owned_devices_v2/endpoints_analysis/'

domains_apps = json.load(open(base_path + 'merged_endpoints.json', 'r'))

def notResolving(hostname):
    try:
        return socket.gethostbyname(hostname) == None
    except UnicodeError as e:
        return True
    except socket.gaierror as e:
        return True


domains = []

for endpoint in domains_apps:
    domains.append(endpoint.strip('www.'))

'''for attr, value in domains_apps.items():
    for attr1,value1 in domains_apps[attr]['domains'].items():
        if attr1 not in domains:
            domains.append(attr1.replace('www.', ''))'''

#print(domains)
error = []
none = []

for dom in domains:
    try:   
        domain = whois.whois(dom)
        print(dom + " -> ", domain.registrar)
        if domain.registrar == None:
            none.append(dom)
    except:
        print(dom + "-> Error")
        error.append(dom)
        
print(none)
print(len(none))
print(error)
print(len(error))
