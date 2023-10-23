import json, re
from operator import truediv

to_check = ['Resources', 'UNKNOWN', 'fromUI.local', 'not_found', '-1', 'Intent_GetExtra->Bundle', 'SharedPreferences_GetDefault', 
        'New<->EditText']

apps = ['bose']
app_name = 'hue'
base_path = '../owned_devices_v2/full_reconstructed/paths/'

#"Intent_GetExtra" + expr.getType() + "->" + expr.getArg(0).toString()
regex_1 = 'Intent_GetExtr.*\-\>.*'
#"Bundle_GetExtra" + expr.getType() + "->" + expr.getArg(0).toString()
regex_2 = 'Bundle_GetExtra.*\-\>.*'
#"SharedPreferences_GetString->" + expr.getArg(0).toString()
regex_3 = 'SharedPreferences_GetString->.*'
#"SharedPreferences_GetExtra" + expr.getType() + "->" + expr.getArg(0).toString()
regex_4 = 'SharedPreferences_GetExtra.*\-\>.*'

def remove_domain(path):

    updated_path = path.strip('https://').strip('http://').split('/')

    result = ''

    for element in updated_path[1:]:
        result += '/' + element

    return result.split('?')[0]


regex_8 = '.*/{3,}.*'

regexs = [regex_1, regex_2, regex_3, regex_4, regex_8]

def check_if_artifact(path):
    for item in to_check:
        if item in path:
            print(path)
            return True
        
    for regex in regexs:
        if re.match(regex, path) != None:
            return True




#"SQLiteDatabase_GetOpen->" + expr.getArg(0).toString()
#"SQLiteDatabase_GetQuery->" + expr.getArg(0).toString()
#"SQLiteDatabase_GetQuery->" + expr.getArg(1).toString()

paths = json.load(open(base_path + app_name + '.json', 'r'))

excluded = 0

valid_paths = []

for path in paths:
    #if check_if_artifact(path):
    #    excluded += 1
    if '<' in path or '{' in path or '"' in path or '\'' in path:
        print(path)
        pass
    elif 'http://' in path or 'https://' in path:
        res = remove_domain(path)
        if res not in valid_paths:
            valid_paths.append(res)
    else:
        if path[0] != '/':
            path = '/' + path
        if path.split('?')[0] not in valid_paths:
            valid_paths.append(path.split('?')[0])

file_matched_paths = open(base_path + "filtered/" + app_name + ".json", "w")
json.dump(valid_paths, file_matched_paths)

print(len(paths))
print(len(valid_paths))
print(valid_paths)
