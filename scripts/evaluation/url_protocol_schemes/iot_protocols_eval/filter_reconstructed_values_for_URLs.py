import json, re, iocextract, ast, time

path = '../verified_iot_datasets/'

excluded_list = ['\n','[]','{}',"  ","        ","      "," ","\r\n"]

EXCLUDED_VALUES = ["HTTP/1.1", "0-0/-1", "/(.*)", "application/json", "application/x-www-form-urlencoded;", "multipart/form-data;", "application/x-gzip", "Android/1.0", 
    "application/json;", "application/x-www-form-urlencoded", "<?xml version=\"1.0\"", "HTTP/2.0", "datatransport/2.2.0", "text/html", "text/plain", "<?xml version=\"1.0\"", "application/octet-stream"]


# REGEX FROM CUCKOO SANDBOX
# https://github.com/cuckoosandbox/cuckoo/blob/master/cuckoo/common/objects.py
URL_REGEX = (
    # HTTP/HTTPS.
    "(https?:\\/\\/)"
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
                    print(url)
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
        print(match)
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

def additional_constraints(element):

    element = element.replace(" ", "")

    #exclude 2 digits numbers (negative numbers?)
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

    if element not in excluded_list and len(element) > 1 and len(match) == 0 and len(match2) == 0:
        return True
    return False

#analyze the requests file

total_reconstructed = []

dataset = 'iotprofiler'

reconstructed_json = json.load(open(path + dataset + '_mqtt_1.json', 'r'))

excluded_counter = 0

for app in reconstructed_json:

    excluded_counter = 0

    print("\nAnalyzing: ", app['app_name'])
    #print(app)
    try:
        #print("Total reconstructed values: ", len(app['reconstructed_values']))
        for value in app['reconstructed_values']:
            if additional_constraints(value):
                sanitized = parse_urls_from_string(value)
                if len(sanitized) > 0:
                    for element in sanitized:
                        if element not in total_reconstructed:
                            total_reconstructed.append(element)
                else:
                    excluded_counter += 1
        #print('Excluded: ', excluded_counter)

        time.sleep(1)
    except:
        print("\nERROR, ", app['app_name'])

print(total_reconstructed)

# reconstructed_values_file = open(path + dataset + '_endpoints_amqp.json', 'w+')
# json.dump(total_reconstructed, reconstructed_values_file)
