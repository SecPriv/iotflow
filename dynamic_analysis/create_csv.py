import json, csv, sys

APP = sys.argv[1]
PATHS_OR_DOMAINS = sys.argv[2]

if PATHS_OR_DOMAINS == 'paths':
    FOLDER_MANUAL_PATHS = '../full_reconstructed/cdf_data/manual_paths/'
    manual = json.load(open(FOLDER_MANUAL_PATHS + APP + '.json', 'r'))

    FOLDER_IOTFLOW_PATHS = '../full_reconstructed/cdf_data/reconstructed_paths/'
    iotflow = json.load(open(FOLDER_IOTFLOW_PATHS + APP + '.json', 'r'))

elif PATHS_OR_DOMAINS == 'domains':
    FOLDER_MANUAL_DOMAINS = '../domains_manual/'
    manual = json.load(open(FOLDER_MANUAL_DOMAINS + APP + '.json', 'r'))

    FOLDER_IOTFLOW_DOMAINS = './iotflow_endpoints/'
    iotflow = json.load(open(FOLDER_IOTFLOW_DOMAINS + APP + '.json', 'r'))

HEADER = ['IOTFLOW', 'DYNAMIC', 'REMOVE']

csv_file = open('./csv_'+ PATHS_OR_DOMAINS + '/' + APP + '.csv', 'w')

writer = csv.writer(csv_file)

print(manual)

writer.writerow(HEADER)

shared = set()

for m in manual:
    print(m)
    if m in iotflow:
        writer.writerow([m,m,""])
        shared.add(m)
    
for m in manual:
    if m not in shared:
        writer.writerow(['',m,''])

for i in iotflow:
    if i not in shared:
        writer.writerow([i, '', ''])

csv_file.close()