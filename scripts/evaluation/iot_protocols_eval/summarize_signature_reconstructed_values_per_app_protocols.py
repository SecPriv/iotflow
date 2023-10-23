import json, re, iocextract, ast, os

base_path = '../verified_iot_datasets/iotscope/IoTSpotter/verified/2023_04_06/requests/'

#Weird reconstructed values to esclude
EXCLUDED_VALUES = ['\n','[]','{}',"  ","        ","      "," ","\r\n", "HTTP/1.1", "0-0/-1", "/(.*)", "application/json", "application/x-www-form-urlencoded;", "multipart/form-data;", "application/x-gzip", "Android/1.0", "application/json;", "application/x-www-form-urlencoded", "<?xml version=\"1.0\"", "HTTP/2.0", "datatransport/2.2.0", "text/html", "text/plain", "<?xml version=\"1.0\"", "application/octet-stream"]

def additional_constraints(element):

    element = element.replace(" ", "")

    #exclude 2 digits numbers 
    regex = "^\d{2}$"
    match = re.findall(regex, element)

    #exclude arrays of 0s
    try:
        array_element = ast.literal_eval(element)
        all_zeros = all([elem == 0 for elem in array_element])
        all_zeros_except_first_element = all([elem == 0 for elem in array_element[1:]])
        if all_zeros or (len(array_element) > 2 and all_zeros_except_first_element):
            return False
    except:
        pass

    #exclude items only made of special chars like - . [ ] etc
    regex2 = "^[\W_]+$"
    match2 = re.findall(regex2, element)

    #check conditions, plus single chars are excluded
    if element not in EXCLUDED_VALUES and len(element) > 1 and len(match) == 0 and len(match2) == 0:
        return True
    return False

# REGEX FROM CUCKOO SANDBOX
# https://github.com/cuckoosandbox/cuckoo/blob/master/cuckoo/common/objects.py
URL_REGEX = (
    # HTTP/HTTPS.
    "(https?:\\/\\/)"
    "(wss?:\\/\\/)"
    "(http?:\\/\\/)"
    "(tcp?:\\/\\/)"
    "(ssl?:\\/\\/)"
    "((["
    # IP address.
    "(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\."
    "(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\."
    "(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\."
    "(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])]|"
    # Or domain name.
    "[a-zA-Z0-9\\.-]+)"
    # Optional port.
    "(\\:\\d+)?"
    # URI.
    "(/[\\(\\)a-zA-Z0-9_:%?=/\\.-]*)?"
)

#CHECK IF VALUE IS A VALID URL/IP

# REGEX TAKEN FROM FILESCAN FOR COMMON URLs https://github.com/giovannipessiva/filescan/blob/master/filescan.py
WHITELIST_REGEX = "(?:(?:(developer|schemas)\.android\.com)|(wc?3\.org)|(apple\.com/DTD)|(apache\.org)|(jquery\.com)|(developers\.facebook\.com))"

# IOCextract has false positives, optionally only look at beginning of string 
SEARCH_STRING_START = False

# Minimum length of strings to look for
MIN_LENGTH = 4

def parse_urls_from_string(raw_string):
    re_ignore = re.compile(WHITELIST_REGEX, re.IGNORECASE)
    re_urls = re.compile(URL_REGEX, re.IGNORECASE)
        
    potential_urls = set()

    for string in raw_string.replace(","," ").replace(";"," ").split():
        if re_ignore.search(string): continue
        
        for url in iocextract.extract_urls(string):
            if SEARCH_STRING_START: 
                if string.startswith(url): 
                    potential_urls.add(url)
            else:
                potential_urls.add(url)
        for ip in iocextract.extract_ips(string):
            if SEARCH_STRING_START: 
                if string.startswith(ip): 
                    potential_urls.add(ip)
            else:
                potential_urls.add(ip)
    
        match = re_urls.search(string)
        if match:
            url = "".join([m for m in match.groups() if m != None])
            potential_urls.add(url)
    
    # TODO: add more sanitizing steps?
    sanitized_urls = []
    for url in potential_urls:        
        while True:     
            sanitized = url
            for char in [")", ".", "/", "\"", "'"]:
                sanitized = sanitized.strip(char) 
            if url == sanitized:
                break
            url = sanitized
            
        while True: 
            head, _sep, tail = sanitized.rpartition("</")
            if head:
                sanitized = head
            else:
                break
        
        if len(sanitized) < MIN_LENGTH: continue
        sanitized_urls.append(sanitized)
        
    return sanitized_urls


apps_and_values = []

#files greater than 1GB
big_apps = []
#JSON encoding error
error_apps = []

# iterate over all the apps files
for app_name in os.listdir(base_path):
    print("Analyzing ", app_name, "...")

    #If file size greater than 1GB don't analyze it, do it only on server
    if (os.stat(base_path + app_name).st_size > 1000000000):
        print("Filesize exceeds 1GB for ", app_name)
        big_apps.append(app_name)
    
    else:
        with open(base_path + app_name, 'r') as appfile:
            app = {}
            
            #try to load JSON file
            try:
                data = json.load(appfile)

                if len(data['ValuePoints']) != 0:
                    app['app_name'] = app_name.strip('.json')

                    signatures = []
                    filtered_values = []
                    
                    # TODO: enable with MQTT
                    #app['usernames'] = []
                    #app['passwords'] = []

                    for valuePoint in data['ValuePoints']:
                        try:
                            for valueSet in valuePoint['ValueSet']:
                                #iterate over keys in valueSet objects
                                for key, attr in valueSet.items():
                                    for reconstructed_value in valueSet[key]:
                                        #Reconstructed values different from empty array and from empty string
                                        if reconstructed_value != "" and reconstructed_value != "[]":
                                            if reconstructed_value not in filtered_values and additional_constraints(reconstructed_value):
                                                #check if reconstructed value contains valid URLs
                                                '''potential_urls = parse_urls_from_string(reconstructed_value)
                                                if len(potential_urls) > 0:
                                                    for potential_url in potential_urls:
                                                        filtered_values.append(potential_url)'''
                                                filtered_values.append(reconstructed_value)
                                                
                            if valuePoint['appendix']['sigatureInApp'] not in signatures:
                                signatures.append(valuePoint['appendix']['sigatureInApp'])

                            #ENABLE WITH MQTT
                            '''signature = valuePoint['appendix']['sigatureInApp']
                            if 'username' in signature or 'Username' in signature or 'UserName' in signature:
                                for valueSet in valuePoint['ValueSet']:
                                    for key, attr in valueSet.items():
                                        for reconstructed_value in valueSet[key]:
                                            app['usernames'].append(reconstructed_value)
                            
                            if 'password' in signature or 'Password' in signature:
                                for valueSet in valuePoint['ValueSet']:
                                    for key, attr in valueSet.items():
                                        for reconstructed_value in valueSet[key]:
                                            app['passwords'].append(reconstructed_value.replace(', ', '').replace('[', '').replace(']', ''))'''
                                
                        except:
                            pass
                        
                    if len(filtered_values) > 0:
                        app['reconstructed_values'] = filtered_values
                        app['signatures'] = signatures
                        apps_and_values.append(app)
            except:
                print("Error in JSON encoding for app: ", app_name)
                error_apps.append(app_name)
        

with open('../verified_iot_datasets/iotspotter_requests.json', 'w') as outfile:
    json.dump(apps_and_values, outfile)

print(len(apps_and_values))

#print(big_apps)
#print(error_apps)