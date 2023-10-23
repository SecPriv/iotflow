import json, re, ast, os

base_path = '../verified_iot_datasets/iotscope/decarli_et_al/2023_04_06/mqtt/'

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


apps_and_values = []

#files greater than 1GB
big_apps = []
#JSON encoding error
error_apps = []

def get_mqtt_attribute(v, a, s):
    if re.match(a, v['appendix']['sigatureInApp'], re.IGNORECASE):
        for valueSet in v['ValueSet']:
            #iterate over keys in valueSet objects
            for key, attr in valueSet.items():
                for reconstructed_value in valueSet[key]:
                    #Reconstructed values different from empty array and from empty string
                    if reconstructed_value != "" and reconstructed_value != "[]" and additional_constraints(reconstructed_value):
                        if reconstructed_value not in s:
                            s.append(reconstructed_value.replace(', ', ''))


# iterate over all the apps files
for app_name in os.listdir(base_path):
#for app_name in app_names:
    print("Analyzing ", app_name, "...")

    #If file size greater than 1GB don't analyze it
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

                    app['usernames'] = []
                    app['passwords'] = []

                    for valuePoint in data['ValuePoints']:
                        get_mqtt_attribute(valuePoint, '.*password.*', app['passwords'])
                        get_mqtt_attribute(valuePoint, '.*username.*', app['usernames'])
                        
                    apps_and_values.append(app)
            except:
                print("Error in JSON encoding for app: ", app_name)
                error_apps.append(app_name)
        
json.dump(apps_and_values, open('../verified_iot_datasets/mqtt_data/mqtt_credentials_neupane.json', 'w'))