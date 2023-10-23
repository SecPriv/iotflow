import json

app_names = ['fitpro', 'bose', 'hama', 'flowercare', 'ikea', 'kindelf', 'lifx', 'nut', 'soundcore', 'hue', 'wiz']

for app_name in app_names:
    file_name = app_name + '_converted.txt'

    traffic_file = open(
        '../monkey/mitmproxy/converted/' + file_name, 'r').readlines()

    #traffic_file = open(
    #    '../results/mitmproxy_traffic/txt_converted/' + file_name, 'r').readlines()

    valuescope_values = json.load(open(
        '../owned_devices_v2/full_reconstructed/'+app_name+'.json', 'r'))

    full_match = []

    # iterate over all the values reconstructed by valuescope
    for value in valuescope_values:
        print("Analyzing: " + value)
        # iterate over all the traffic file
        matched_lines = []
        for traffic_line in traffic_file:
            single_match = {}
            # if the reconstructed value is in any of the line of the traffic file then add that
            if value in traffic_line:
                print('found occurence!')
                matched_lines.append(traffic_line)

        single_match = {'reconstruced_value': value,
                        'matched_lines': matched_lines}
        if len(matched_lines) > 0:
            full_match.append(single_match)

    output = open(
        '../owned_devices_v2/comparison_results/full_match/monkey/'+app_name+'.json', 'w+')
    json.dump(full_match, output)
