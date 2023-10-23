#!/usr/bin/env python3
import re
import json
from unittest import result

import iocextract

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

def parse_url_params_from_string(raw_string):
    raw_string = raw_string.replace("\"", "")
    #result = re.search("[^\<]\?.*=", raw_string)
    result = re.search("\?[^xml].*=", raw_string)
    if result != None and raw_string not in EXCLUDED_VALUES and "AND" not in raw_string:
        return raw_string

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True
       
def parse_request_body(raw_string):

    validJSON = validateJSON(raw_string)

    result = re.search("{.*?}", raw_string)
    if result != None and validJSON:
        return raw_string
    
def parse_paths(raw_string, matched_paths):

    possible_paths = []

    raw_string = raw_string.replace("<br/>","")
    for string in raw_string.split():
        #TODO: not sure about removing also ,\. since it removes a lot of things and might be too much
        result = re.search(".*[^/]/[^/].*", string)

        if result != None and string not in EXCLUDED_VALUES and string not in matched_paths:
            possible_paths.append(string)

    return possible_paths

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
    sanitized_urls = set()
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
        sanitized_urls.add(sanitized.strip("/"))
        
    return sanitized_urls
    
    
def main():

    #TODO: bit of sanitiatization to exclude false positives and test it
    #TODO: avoid repeating values inside the lists
    matched_URLS = []
    matched_URLS_params = []
    matched_request_body = []
    matched_paths = []

    app_name = "wiz"

    for item in json.load(open("../owned_devices_v2/full_reconstructed/"+ app_name + ".json", "r")):
    
        #URLs = parse_urls_from_string(item)
        #if len(URLs) > 0 and URLs not in matched_URLS:
        #    matched_URLS.append(URLs)

        #if parse_url_params_from_string(item) != None and item not in matched_URLS_params:
        #    matched_URLS_params.append(item)
        
        #if parse_request_body(item) != None and item not in matched_request_body:
        #    matched_request_body.append(item)

        #item not in matched urls does not work since it is a list of objects
        if len(parse_paths(item, matched_paths)) > 0:
            matched_paths = matched_paths + parse_paths(item, matched_paths)

    base_path = "../owned_devices_v2/full_reconstructed/"

    #print(matched_URLS)
    #print(len(matched_URLS))
    #file_matched_urls = open(base_path + "urls/" + app_name + ".txt", "w")
    #file_matched_urls = open(base_path + "urls_requests_missing.txt", "w")
    #file_matched_urls.write(str(matched_URLS))

    '''#print(matched_URLS_params)
    print(len(matched_URLS_params))
    file_matched_urls_params = open(base_path + "urlsParams/" + app_name + ".json", "w")
    json.dump(matched_URLS_params, file_matched_urls_params)
    
    #print(matched_request_body)
    print(len(matched_request_body))
    file_matched_bodies = open(base_path + "bodies/" + app_name + ".json", "w")
    json.dump(matched_request_body, file_matched_bodies)'''

    #print(matched_paths)
    print(len(matched_paths))    
    file_matched_paths = open(base_path + "paths/" + app_name + ".json", "w")
    json.dump(matched_paths, file_matched_paths)

if __name__ == '__main__':
    main()
