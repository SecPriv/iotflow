
import logging
import json
import argparse
import sys
import os
import re
import tldextract


invalidEndings = ["box", "php","zip","card","medal","UserDevicesGet","AddSound","Backome","image","renderer","memo","calendar","saveWallPhoto","asm","LiveviewSrc","presence","bin","svc","refreshProviderSession","reportSDKError","setAccountInfo","refreshProviderSession","removeConnection","asf","CGI","sendSeekEnd","adEnd","rendered","failed","nick","gid","changed","status","rule","naver","sdp","amp","setBitrateKbps", "adStart","init","reportError","cleanupSession","retrieve","setPlayerState","sendSeekStart","createSession","attachPlayer","reset","asset","failure","success","tflite", "mpd","device","recipient","srf","find","autocomplete","reference","gif","get", "action","getTokenInfo","htm","html","getResponseCode", "library","replace","viewablejs", "sdk", "https", "deviceId", "useBrowserForAuthorization", "scope", "checkAPIKey", "ssoVersion", "clietId", "redirectURI", "code", "directedId", "profile", "sandbox", "returnCode", "noService", "sdkVersion"]

invalidDomains = set()

def setUpArgParser():
    parser = argparse.ArgumentParser(description='Analyse some leak scope results')
    parser.add_argument('-o', '--output', required=True, help='Output directory', type=str)
    parser.add_argument('-f', '--input-file', required=False, help='Input json file with the results from LeakScope', type=str)
    parser.add_argument('-d', '--input-dir', required=False, help='Input directory containing json results from LeakScope', type=str)
    return parser



def isInvalidEnding(domain):
    for s in invalidEndings:
        if domain.endswith(s):
            return True
    return False


def getJsonFromFile(path):
    with open(path) as json_file:
        try:
            return json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            logging.error('json loading failed for {} with exception {}'.format(path, e))
            return None



def getUniqueSubDomainsFromLeakScope(path):
    data = getJsonFromFile(path)
    if data == None:
        return

    return getUniqueSubDomainsFromJson(data)


def getUniqueSubDomainsFromJson(data):
    """
    docstring
    """
    notFound = []
    result = set()
    if 'ValuePoints' not in data:
        return result

    for valuePoint in data['ValuePoints']:
        valueSet = None
        if not 'ValueSet' in valuePoint:
            continue


        for valueSet in valuePoint['ValueSet']:
            if len(valueSet) == 0:
                continue

            for key in valueSet.keys():
                for value in valueSet[key]:
                    for comma in value.split(","):
                        for v in comma.split('||'):
                            logging.debug("handling {}".format(v))
                            v = v.replace('NOT_FOUND', '')
                            v = v.replace('.json', '')
                            v = v.replace('.html', '')
                            v = v.replace('.php', '')
                            v = v.replace('.jpg', '')
                            v = v.replace('.png', '')
                            v = v.replace('.cgi', '')
                            v = v.replace('.aspx', '')
                            v = v.replace('.asp', '')
                            v = v.replace('.smp', '')
                            v = v.replace('.xml', '')
                            v = v.replace('.cfg', '')
                            v = v.replace('UNKNOWN', '')


                            domain = re.findall('([a-zA-Z0-9][a-zA-Z0-9-\.]{1,200}\.[a-zA-Z]{2,})', v)
                            ip = re.findall('(\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)', v)

                            # test
                            if domain != None:
                                for d in domain:
                                    domainString = str(d)
                                    domainString = domainString.replace('www.', '')

                                    if ".local" in domainString or domainString in notFound:
                                        continue

                                    extracted = tldextract.extract(domainString)

                                    if domainString not in result and not isInvalidEnding(domainString) and extracted.suffix != '':
                                        result.add(domainString)
                                        logging.debug("found domain {}".format(domainString))

                            if ip != None:
                                for i in ip:
                                    ipString = str(i)

                                    logging.debug("found an ip address {}".format(ipString))
                                    #if localNetwork.match(ipString) or localIp.match(ipString):
                                    #    logging.debug("matched an local ip address")
                                    #    continue
                                    result.add(ipString)
                                    logging.debug("found ip {}".format(ipString))


            # alternatively get keys with valueSet.keys but as far as i found it is not guaranteed that they are ordered


    return result


def writeJson(stats, file):
    if stats == {}:
        logging.debug("No countries found for {}".format(file))
        return
    with open(file, 'w') as outfile:
        json.dump(stats, outfile)

def getFileName(filename):
    filename = filename.replace('.json',  '')
    splittedFile = filename.split('/')
    return splittedFile[len(splittedFile) -1]



def writeAllToFiles(results, filenames ,outputDir):
    for i in range(0, len(results)):
        writeJson(list(results[i]), outputDir +'/' + filenames[i] + '.json')


def extractAllFromDirectory(dirInput):
    resultsDomain = []
    fileNames = []
    for f in os.scandir(dirInput):
        f = f.name
        print("loading: " + f)
        if f.endswith('json'):
            #getUrlsFromLeakScope(f)
            appName = getFileName(dirInput + f)
            domains = getUniqueSubDomainsFromLeakScope(dirInput + f)
            resultsDomain.append(domains)
            fileNames.append(appName)

    return resultsDomain, fileNames



def getUniqueDomainDataFromLeakScope(path):

    notFound = []
    result = set()
    with open(path) as json_file:
        data = None
        try:
            data = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            logging.error('json loading failed for {} with exception {}'.format(path, e))
            return result
        if 'ValuePoints' not in data:
            return result

        for valuePoint in data['ValuePoints']:
            valueSet = None
            if not 'ValueSet' in valuePoint:
                continue


            for valueSet in valuePoint['ValueSet']:
                if len(valueSet) == 0:
                    continue

                for key in valueSet.keys():
                    for value in valueSet[key]:
                        for comma in value.split(","):
                            for v in comma.split('||'):
                                #print(v)
                                logging.debug("handling {}".format(v))
                                v = v.replace('NOT_FOUND', '')
                                v = v.replace('.json', '')
                                v = v.replace('.html', '')
                                v = v.replace('.php', '')
                                v = v.replace('.jpg', '')
                                v = v.replace('.png', '')
                                v = v.replace('.cgi', '')
                                v = v.replace('.aspx', '')
                                v = v.replace('.asp', '')
                                v = v.replace('.smp', '')
                                v = v.replace('.xml', '')
                                v = v.replace('.cfg', '')

                                localNetwork = re.findall("(192\.168\.\d\d?\d?\.\d\d?\d?)|(10\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)|(172\.1[6-9]\.\d\d?\d?\.\d\d?\d?)|(172\.2[0-9]\.\d\d?\d?\.\d\d?\d?)|(172\.3[0-1]\.\d\d?\d?\.\d\d?\d?)|(.*[^:]fromUI\.local[:\/ ])", v)
                                if localNetwork != None:
                                    for finding in localNetwork:
                                        for local in finding:
                                            local = local.replace(':', '')
                                            local = local.replace('/', '')
                                            local = local.replace('https', '')
                                            local = local.replace('http', '')

                                            if len(local) > 2 and local not in result:
                                                if ("fromUI.local" not in local or ("fromUI.local" in local and len(local) == len("fromUI.local"))):
                                                    #print(local)
                                                    result.add(local)



                # alternatively get keys with valueSet.keys but as far as i found it is not guaranteed that they are ordered


    return result


def main():

    parser = setUpArgParser()
    options = parser.parse_args()

    if options.input_file == None and options.input_dir == None:
        parser.print_help()
        sys.exit(1)
    elif options.input_file != None:
        appName = getFileName(options.input_file)
        domains = getUniqueSubDomainsFromLeakScope(options.input_file)
        writeJson(list(domains), options.output + appName + '.json')
    else:
        overallMap = {}
        domains, filenames = extractAllFromDirectory(options.input_dir)
        writeAllToFiles(domains, filenames, options.output)


        #writeJson(overallMap, options.output  + 'overall' + '.json')

if __name__ == "__main__":
    main()


