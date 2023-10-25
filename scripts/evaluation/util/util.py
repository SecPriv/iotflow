import socket
import json
import logging
import os
import tldextract
import re

manual = ["com.tuya.smartlife", "com.garmin.android.apps.connectmobile", "com.bshg.homeconnect.android.release",
          "com.huawei.health", "com.philips.ka.oneka.app", "com.google.android.apps.chromecast.app",
          "com.amazon.kindle", "jp.co.canon.bsd.ad.pixmaprint", "com.huami.watch.hmwatchmanager",
          "com.google.android.wearable.app", "com.sonos.acr2", "com.veryfit2hr.second", "com.amazon.dee.app",
          "com.aldi_project", "com.soomapps.screenmirroring", "com.irobot.home", "com.lgeha.nuts",
          "com.google.android.apps.fitness", "com.tuya.smart", "com.tonies.app", "com.hp.printercontrol",
          "com.garmin.connectiq", "com.crrepa.band.dafit", "jp.co.canon.android.printservice.plugin",
          "com.amazon.storm.lightning.client.aosp", "ir.remote.smg.tv", "com.vorwerk.cookidoo", "com.xiaomi.smarthome",
          "screen.mirroring.screenmirroring", "com.playstation.remoteplay", "jbl.stc.com", "com.tplink.iot",
          "com.strava", "com.hdvideoprojector.screenmirroring.castvideototv",
          "com.universal.tv.remote.control.all.tv.controller", "com.OnSoft.android.BluetoothChat",
          "plus.home_connect.android", "com.govee.home", "com.tplink.tether", "com.hp.android.printservice",
          "com.casttotv.screenmirroring.smarttv.castvideo", "soulapps.screen.mirroring.smart.view.tv.cast",
          "com.lscsmartconnection.smart", "at.a1.android.iapp", "epson.print", "com.sony.songpal.mdr",
          "com.hdvideoplayer.screencasting.simulator", "com.runtastic.android", "com.scee.psxandroid",
          "com.microsoft.xboxone.smartglass"]

applist = ['com.OnSoft.android.BluetoothChat', 'com.amazon.storm.lightning.client.aosp',
           'com.bshg.homeconnect.android.release', 'com.garmin.android.apps.connectmobile',
           'com.google.android.apps.chromecast.app', 'com.google.android.apps.googleassistant',
           'com.google.android.wearable.app', 'com.hp.android.printservice', 'com.huawei.health', 'com.irobot.home',
           'com.lgeha.nuts', 'com.soundcloud.android', 'com.tplink.tether', 'com.tuya.smart', 'com.tuya.smartlife',
           'com.xiaomi.hm.health', 'com.xiaomi.smarthome', 'epson.print', 'ir.remote.smg.tv',
           'jp.co.canon.android.printservice.plugin']

all_excluded_apps = []
all_excluded_apps.extend(manual)
all_excluded_apps.extend(applist)


class AppAnalysis:
    def __init__(self, path, app, skip=False):
        for a in all_excluded_apps:
            if a in app:
                if skip:
                    self.skip = True
                    return
                print(f"WARNING {a} in {app} app list")
        self.skip = False
        self.app = app
        self.path = path
        self.amqp = getJsonData(f"{path}/amqp/{app}")
        self.coap = getJsonData(f"{path}/coap/{app}")
        self.endpoints = getJsonData(f"{path}/endpoints/{app}")
        self.mqtt = getJsonData(f"{path}/mqtt/{app}")
        self.xmpp = getJsonData(f"{path}/xmpp/{app}")
        self.udp = getJsonData(f"{path}/udp/{app}")
        self.crypto = getJsonData(f"{path}/crypto/{app}")
        self.webview = getJsonData(f"{path}/webview/{app}")
        self.sources = getJsonData(f"{path}/sources/{app}")
        self.sinks = getJsonData(f"{path}/sinks/{app}")


def filter_apps(dataset, name, mapping):
    result = []
    for app in dataset:
        app_name = app.app
        app_name = app_name[0:len(app_name) - 5]
        if app_name in mapping:
            if mapping[app_name] == name:
                result.append(app)
        else:
            result.append(app)
    return result


def get_all_files(path):
    result = set()
    result.update(os.listdir(f"{path}/amqp/"))
    result.update(os.listdir(f"{path}/coap/"))
    result.update(os.listdir(f"{path}/endpoints/"))
    result.update(os.listdir(f"{path}/mqtt/"))
    result.update(os.listdir(f"{path}/xmpp/"))
    result.update(os.listdir(f"{path}/udp/"))
    result.update(os.listdir(f"{path}/webview/"))
    return result


def loadAllData(path, skip=False):
    result = []
    for app in get_all_files(path):
        appAnalysis = AppAnalysis(path, app, skip)
        if not appAnalysis.skip:
            result.append(appAnalysis)

    return result


def get_verified_dataset(path_prefix, path_extension, mapping):
    mapping_json = {}
    with open(mapping, "r") as f:
        mapping_json = json.load(f)
    neupane_dataset = loadAllData(path_prefix + "/neupane/" + path_extension)
    iotspotter_dataset = loadAllData(path_prefix + "/iotspotter/" + path_extension)
    iotprofiler_dataset = loadAllData(path_prefix + "/iotprofiler/" + path_extension)
    print(len(neupane_dataset))
    neupane_dataset = filter_apps(neupane_dataset, "neupane", mapping_json)
    print(len(neupane_dataset))

    print(len(iotspotter_dataset))
    iotspotter_dataset = filter_apps(iotspotter_dataset, "iotspotter", mapping_json)
    print(len(iotspotter_dataset))

    print(len(iotprofiler_dataset))
    iotprofiler_dataset = filter_apps(iotprofiler_dataset, "iotprofiler", mapping_json)
    print(len(iotprofiler_dataset))

    return neupane_dataset + iotspotter_dataset + iotprofiler_dataset


def mergeDicts(dict1, dict2):
    result = {}
    keyList = list(dict1.keys())
    keyList.extend(list(dict2.keys()))
    keyValues = set(keyList)
    # Done for both, if dict1 is missing key x and
    for k in keyValues:
        result[k] = dict1.get(k, 0) + dict2.get(k, 0)

    return result


def getFileName(filename):
    filename = filename.replace('.json', '')
    splittedFile = filename.split('/')
    return splittedFile[len(splittedFile) - 1]


def getJsonData(path):
    if not os.path.exists(path):
        return {}
    with open(path) as json_file:
        data = {}
        try:
            data = json.load(json_file)
            return data
        except json.decoder.JSONDecodeError as e:
            logging.error('json loading failed for {} with exception {}'.format(path, e))
            return data


def getJsonFile(path):
    with open(path) as json_file:
        data = None
        try:
            data = json.load(json_file)
            return data
        except json.decoder.JSONDecodeError as e:
            logging.error('json loading failed for {} with exception {}'.format(path, e))
            return data


def writeJson(stats, file):
    if stats == {}:
        logging.debug("No countries found for {}".format(file))
        return
    with open(file, 'w') as outfile:
        json.dump(stats, outfile)


def getUniqueDomainsFromJson(data):
    """
    docstring
    """
    result = set()
    if 'ValuePoints' not in data:
        return result

    for valuePoint in data['ValuePoints']:
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
                                    result.add(domainString)

                            if ip != None:
                                for i in ip:
                                    ipString = str(i)
                                    result.add(ipString)

    return result


def getUniqueLocalCommunicationJson(data):
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
                            # print(v)
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
                            v = v.lower()

                            localNetwork = re.findall(
                                "(192\.168\.\d\d?\d?\.\d\d?\d?)|(10\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)|(172\.1[6-9]\.\d\d?\d?\.\d\d?\d?)|(172\.2[0-9]\.\d\d?\d?\.\d\d?\d?)|(172\.3[0-1]\.\d\d?\d?\.\d\d?\d?)|(.*[^:]fromui\.local[:\/ ])|(fd00:)|(fe80:)|(fc00:)",
                                v)
                            if localNetwork != None:
                                for finding in localNetwork:
                                    for local in finding:
                                        local = local.replace(':', '')
                                        local = local.replace('/', '')
                                        local = local.replace('https', '')
                                        local = local.replace('http', '')

                                        if local.startswith("f") and "from" not in local:
                                            local = local + ":"

                                        if len(local) > 2 and local not in result:
                                            if ("fromui.local" not in local or (
                                                    "fromui.local" in local and len(local) == len("fromui.local"))):
                                                # print(local)
                                                result.add(local)

            # alternatively get keys with valueSet.keys but as far as i found it is not guaranteed that they are ordered

    return result


def getTldResultsWithoutLocal(data):
    result = set()
    for domain in data:
        if hasTldSuffix(domain) and not isLocal(domain):
            result.add(domain)

    return result


def getTldResultsWithLocal(data):
    result = set()
    for domain in data:
        if hasTldSuffix(domain):
            result.add(domain)

    return result


def hasTldSuffix(domain):
    extracted = tldextract.extract(domain)
    return extracted.suffix != ''


localNetwork = re.compile(
    "(192\.168\.\d\d?\d?\.\d\d?\d?)|(10\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)|(172\.1[6-9]\.\d\d?\d?\.\d\d?\d?)|(172\.2[0-9]\.\d\d?\d?\.\d\d?\d?)|(172\.3[0-1]\.\d\d?\d?\.\d\d?\d?)|(.*[^:]fromui\.local[:\/ ])|(fd00:)|(fe80:)|(fc00:)")
localIp = re.compile("(^127\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?.*)|(^(.*:?\/?\/?)::1.*)|(^0\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?.*)")
ip = re.compile("\d\d?\d?.\d\d?\d?\.\d\d?\d?\.\d\d?\d?")


def getDomainOrIP(d):
    extractedSubdomain = tldextract.extract(d)
    if ip.match(extractedSubdomain.domain):
        return extractedSubdomain.domain
    return extractedSubdomain.domain + '.' + extractedSubdomain.suffix


def isLocal(d):
    dl = d.lower()
    if localNetwork.match(dl) or localIp.match(dl) or '.local' in dl:
        return True

    return False


def domainsWithoutLocal(data):
    result = set()
    data = getTldResultsWithoutLocal(data)
    for domain in data:
        result.add(getDomainOrIP(domain))
    return result


def getAllDataWithoutRequests(app):
    result = set()
    result.update(getUniqueDomainsFromJson(app.amqp))
    result.update(getUniqueDomainsFromJson(app.coap))
    result.update(getUniqueDomainsFromJson(app.endpoints))
    result.update(getUniqueDomainsFromJson(app.mqtt))
    result.update(getUniqueDomainsFromJson(app.xmpp))
    result.update(getUniqueDomainsFromJson(app.udp))
    result.update(getUniqueDomainsFromJson(app.webview))

    return result


def getAllDataDataset(dataset):
    result = []
    for app in dataset:
        result.append(getAllDataWithoutRequests(app))
    return result


def getAllValueSets(jsonData):
    results = set()
    if jsonData == None:
        return results
    if 'ValuePoints' in jsonData:
        for valuePoint in jsonData['ValuePoints']:
            if 'ValueSet' in valuePoint:
                for valueSet in valuePoint['ValueSet']:
                    for k in valueSet.keys():
                        for item in valueSet[k]:
                            results.add(item)
    return results


def getNumberOfValueSets(app):
    result = set()
    result.update(getAllValueSets(app.amqp))
    result.update(getAllValueSets(app.coap))
    result.update(getAllValueSets(app.endpoints))
    result.update(getAllValueSets(app.mqtt))
    result.update(getAllValueSets(app.xmpp))
    return result
