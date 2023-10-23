import re
import json
import socket

app_names = ['ikea', 'bose', 'divoom', 'fitbit', 'fitpro', 'flowercare', 'hama', 'hue', 'ikea', 'kindelf', 'lifx', 'nut', 'soundcore', 'wiz']

domains = []
paths = []
params = []
contents = []
wrong_contents = []

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

for app_name in app_names:

    mitmproxy_txt = open(
        '../monkey/mitmproxy/converted/' + app_name + '_converted.txt', 'r').readlines()

    for i in range(0, len(mitmproxy_txt)):
        # parse the API path
        if "request = " in mitmproxy_txt[i]:
            line = mitmproxy_txt[i]

            request_path = line.replace("request = Request(", '')
            request_path = request_path.replace(')\n', '').replace(
                "  GET", '').replace("  POST", '').replace("  PUT", '')
            request_path = request_path.replace(
                ':80', '').replace(":443", '').replace(" ", '')

            request_path_splitted = request_path.split('/')
            
            domain = request_path_splitted[0].replace('OPTIONS', '')
            if domain not in domains:
                domains.append(domain)


            #remove URL params from the path
            path = request_path.split(request_path_splitted[0])[1].split('?')[0]
            path = path.replace('//', '/')
            if path not in paths:
                paths.append(path)

            result = re.search("\?[^xml].*=", request_path)
            if result != None and request_path not in params:
                params.append(request_path)

        # parse the content of the request
        '''if "'content':" in mitmproxy_txt[i] and "'response': {" not in mitmproxy_txt[i]:
            content = mitmproxy_txt[i]
            while "'headers':" not in mitmproxy_txt[i]:
                i += 1
                if "'headers':" not in mitmproxy_txt[i]:
                    content += mitmproxy_txt[i].replace('\n', '').replace(" ", '')
            content = content.replace('\n', '').replace("'b'", '').replace(
                "content'", '').replace("}}", "}").replace('\\n', '').replace('\\\\', '')
            if content != "                   ': b'',":
                #print(repr(content))
                content = content.replace(' ', '')[4:-2]
                if content not in contents and validateJSON(content):
                    contents.append(content)
                else:
                    if content not in wrong_contents:
                        #print(content + '\n')
                        wrong_contents.append(content)'''


#print(domains)
print(paths)
    #print(params)

    #print(contents)

print("the # of domains found for %s is %d" % (app_name, len(domains)))
    #print("the # of URL params found for %s is %d" % (app_name, len(params)))
    #print("the # of JSON bodies found for %s is %d" % (app_name, len(contents)))
print("the # of paths found for %s is %d" % (app_name, len(paths)))
