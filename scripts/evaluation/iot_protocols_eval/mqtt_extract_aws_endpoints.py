import json


DATASETS = ['iotprofiler', 'iotspotter', 'neupane']

unique_endpoints = set()

for d in DATASETS:
    reconstructed_values = json.load(open(d + '_mqtt.json'))
    for app in reconstructed_values:
        for v in app['reconstructed_values']:
            if 'amazonaws.com' in v:
                unique_endpoints.add(v)

print(unique_endpoints)
