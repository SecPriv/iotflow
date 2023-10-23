import plotly.graph_objects as go
import json
import os
import argparse
import re
import logging
import util.util as util
import requests
import importlib
import json

# manual_endpoints = json.load(open('domains_manual.json'))
# iotscope_endpoints = json.load(open('endpoints_iotscope.json'))

from util.domainUtil import getSanitzedApps, generateTotalCountMapping, getDomainOrIP
from util.domainCategorizationUtil import isAdCategory, isCdnCategory, isSocialNetworkCategory, isAdCategoryNew, isCdnCategoryNew, isSocialNetworkCategoryNew

def getExodusCategories():
    result = {}
    exodusList = json.loads(requests.get("https://reports.exodus-privacy.eu.org/api/trackers").text)
    for _,item in exodusList['trackers'].items():
        currentSet = set()
        for x in item['network_signature'].split('|'):
            if len(x) == 0:
                continue
            x = x.replace('.*', '')
            x = x.replace('\\', '')
            if x.startswith('.'):
                x = x[1:]

            currentSet.add(x)
        if len(currentSet) == 0:
            continue
        if len(item['categories']) == 0:
            tmp = result.get('otherExodus', set())
            for x in currentSet:
                tmp.add(x)
            result['otherExodus'] = tmp
        
        for c in item['categories']:
            tmp = result.get(c, set())
            for x in currentSet:
                tmp.add(x)
            result[c] = tmp
    
    return result

exodusCategories = getExodusCategories()

#iotRelated = {"mob.com", "earthcam.com", "ikonkekit.com", "eye4.cn", "lgsmartplatform.com", "besmart-home.com", "everhome.cloud", "keenhome.io", "myskybell.com", "smarter.am", "hager-iot.com", "plc-smarthome.de", "leaksmart.com", "airpatrol.eu", "tp-link.com", "vesync.com", "airpatrol.eu", "samsungheartwise.com", "myfoscam.cn", "runkeeper.com", "iruniversalremote.com", "apsrvd.io", "remote-app-tv.com", "reolink.com", "neur.io", "futlight.com", "haikuhome.com", "ute-tech.com.cn", "xwemo.com", "myhager.com", "sec-smartswitch.com", "kalay.tw", "lgeaircon.com", "harmankardon.com", "getkuna.com", "withings.com", "prolink2u.com", "anymote.io", "asus-aicam.com", "tplinknbu.com", "lgmobiletv.com", "gemmy.com", "videoloft.com", "epson.net", "totwoo.com", "ambiclimate.com", "ecamzone.cc", "hostedcloudvideo.com", "chuango.cn", "swann.com", "hubbleconnected.com", "lgecloud.com", "yalelock.com", "apexisalarm.com", "alarm.com", "my-gogogate.com", "doorguard.com.au", "devismart.com", "tih.tw", "al8.co", "nucleuslife.io", "vphband.com", "vstarcam.cn", "subli-med.com", "zmodo.com", "wisenetlife.com", "libratone.com", "ihconfig.com", "rabootec.com", "miui.com", "nightowlconnect.com", "cloudwarm.net", "broadlink.com.cn", "keeprapid.com", "reolink.us", "lifesense.com", "simpledesign.ltd", "hager.fr", "simplisafe.co.uk", "iotdreamcatcher.net", "amazonalexa.com", "omguard.com", "xfinity.com", "beonhome.com", "yunjktech.com", "verizonwireless.com", "keeprapid.com", "commax.com", "audiopro.com", "abhijitvalluri.com", "net2point.com", "jimicloud.com", "zositech.com", "alcidae.com", "asuscomm.cn", "meari.com.cn", "kptncook.com", "augustint.com", "connectedfamilyhome.com", "yunyis.com", "getawair.com", "libratone.com.cn", "kalay.net.cn", "sengledcanada.com", "wifly-city.com", "sensicomfort.com", "blazeautomation.com", "neatorobotics.com", "ichano.com", "perimetersafe.com", "nightowlsp.com", "candy-hoover.com", "e-seenet.com", "ipcent.com", "wifiplug.co.uk", "mansaa.io", "asante.com", "mearicloud.com", "cloudant.com", "tendinsights.com", "incardoc.com", "shadeconnector.com", "tiktime.net", "bonlink.com.cn", "vstarcam.com","bose.com", "tuyaeu.com", "divoom-gz.com", "huahuacaocao.com", "103.235.46.40", "nutspace.com", "wizconnected.com", "jusonsmart.com", "umsns.com", "wiz.world", "wizconnected.com", "bose.io", "lifx.api.kustomerapp.com", "gulaike.com", "mi-img.com",'puwell.com', 'getqardio.com','gumplay.jp', 'chuango.com','manything.com','two-commas.com','203.195.160.110', 'tiqiaa.com', 'xiaomi.com',  'huawei.com', 'asus.com','logitech.com', 'samsungapps.com','lifx.com', 'philips.com','sony.com','mi.com','breezometer.com','palmerperformance.com', 'oppodigital.com','xiaoyi.com','ihaus.de','linquet.com','netvue.com','simplisafe.com','ikonke.com', 'mipcm.com', 'sony.co.jp', 'scinan.com', 'airtouch.com.au', 'pindora.fi', 'tado.com', 'tplinkmifi.net', 'hipcam.org','openhab.org','ttlock.com.cn',  'grundfos.com','mytenvis.com','huawei.health', 'goyourlife.com.cn',   'air-stream.com.au', 'pyronixcloud.com', 'dongha.cn',  'intesishome.com','gm.com',  'connected.baby', 'tutk.com', 'winkapp.com','gatelabs.co',  'yolanda.hk','wuudis.com','samsungsmartappliance.com','aylanetworks.com', 'heclouds.com','miwifi.com', 'almando.com','simplehuman.com',  'fitbit.com', 'home-connect.com','asuscomm.com', 'magichue.net','dropcam.com', 'domoticz.com','discovergy.com', 'clearblade.com','dronelogbook.com','ulikespk.com','longitude-watch.com','thieye.com','hom.ee','yalereallivingconnect.com', 'ihomeaudio.com',  'eero.com', 'mobihealthplus.com', 'sosocam.com','hpsmart.com','lokly.com', 'zmote.io','asuscloud.com', 'hpsmartstage.com',  'lge.com','awair.is', 'revolar.net', 'sensornetworks.co.za','allterco.com','thekeywe.com', 'm2mbackup.com', 'xm030.cn',  'traffictechservices.com','roku.com',  'oruibo.com', 'thingsview.net','hetangsmart.com', 'nightowldvr04.com','creative.com','polar.com', 'strava.com', 'nvdvr.cn','readyforsky.com', 'alarmdealer.com',  'ustream.tv','hp.com','philips-healthsuite.com.cn','myharmony.com','ifttt.com','amazfit.com','ogemray-server.com','umeye.com', 'xingcon.com','parrot.com', 'i-sens.co.kr','cloudrail.com',  'prestigio.com', 'amazon.com', 'sensiapi.io','bluedriver.com','birdytone.com', 'dev-myqnapcloud.com', 'doorbird.com',  'ifavine.com', 'usmeew.com', 'iotcplatform.com',  'doorbird.net', 'mindolife.com','actitens.com','triggi.com', 'hpsmartpie.com',  'eyez-on.com', 'linakcloud.com','mobvoi.com','dvr163.com', 'airdata.com', 'nightowlx.com', 'digixvideo.com',  'harman.com','tookok.cn', 'ezvizru.com', 'mydlink.com', 'kef.com','qnap.com.cn','huami.com','ichano.cn','beewi-home.com', 'cosa.com.tr', 'smarthome.com','linksys.com',  'autonat.com','alula.net', 'zipato.com', 'petcube.com','whistle.com', 'filtrete.com', 'dinsafer.com','ebikemotion.com', 'iquarius.com', 'nest.com', 'ictun.com','elinkthings.com','mddcloud.com','netesee.com','ikea.com', 'remoteble.com','skycentrics.com','chschs.com', 'mymili.com',  'y-cam.com','orvibo.com','sciener.com','egardia.com','amazon.co.uk', 'gazeeka.com.au',  'thingsview.co', 'bryant.com', 'goabode.com', 'vimtag.com', 'agaveha.com','myqnapcloud.com','trustsmartcloud.com','air.properties','zhiduodev.com','getdoorbird.com','aicare.net.cn','dooya.com', 'sengled.com','heyitech.com','allegrosmart.com', 'amazon.cn','action.new', 'hover1-app.com','routerlogin.net',  'routethis.co', 'childrenview.net', 'boschtt-documents.com','insteon.com', 'amazon.fr', 'gardena.com', 'vineconnected.com', 'asus.com.cn','flic.io',  'kiwi.ki','ibroadlink.com', 'sony.net', 'sfty.com', 'reco4life.com','enaikoon.de','yitechnology.com','midea.com','homescenario.com',  'sentrolcloud.com','hicloud.com',  'hicling.com','ikea.net','linksyssmartwifi.com','meethue.com', 'mypump.info', 'sonos.com', 'amazon.in','lifx.co','netgear.com', 'ipcam.so','mimoto.it','resideo.com','honeywell.com','tocaboca.com',  'yamaha.com',  'goolink.org', 'earin.com','doorbell.io', 'castify.tv', 'qnap.com', 'smart-me.com',  'm2mservices.com','nuki.io',   'b1automation.com', 'kankun-smartplug.com','ihomeaudiointl.com', 'mynuheat.com', 'wallflower.io', 'revogi.com',  'dlink.com',  'aztech.com','alarm.com', 'chipolo.net','eco-plugs.net',  'ora.vn','garagedoorbuddy.com','snsr.net',  'mobiteka.pl', 'iotworkshop.com', 'linkalock.com', 'myspotcam.com', 'wattwatchers.com.au', 'ecobee.com','commax.co.kr',  'sciener.cn',  'loco.hk', 'august.com', 'wattio.com', 'tivo.com', 'aplombtechbd.com',   'lgthinq.com', 'wink.com', 'ipc365.com', 'fivasim.com', 'eufylife.com',    'ticwear.com',   'alarmnet.com', 'guardingvision.com', 'rcti.es','xiaomi.net',  'amazon.co.jp','goyourlife.com','routethis.com',  'ablecloud.cn','skyward.io','ipcamlive.com', 'bluecats.com','jellyfishtur.cn','ezvizlife.com', 'remotexy.com', 'idevicesinc.com', 'linkplay.com',  'opple.com', 'koogeek.com','iwhop.com', 'logi.com', 'meross.com',  'appnimator.com', 'electricimp.com', 'getblueshift.com', 'mein-henry.de', 'ihomecontrol.de','tomtom.com','bn-link.com','artik.cloud', 'tenvis.com', 'samsung.com','miot-spec.org', 'philips-digital.com',  'ween.fr','chipolo.com', 'roc-connect.com', 'dy1000.com', 'securesmart.cn', 'smanos.com', 'mangocam.com', 'appmifile.com',  'sleepace.net', 'cranesportsconnect.com','trafficland.com',  'rialtocomfort.com',   'myfieldnet.com', 'energy-aware.com', 'wificam.org',  'ieiworld.com','myedimax.com', 'muzzley.com', 'u-blox.com','carrier.com','neolock.vn', 'securemote.com', 'sense-u.com','yeelight.com', 'epson.com', 'feetguider.com', 'netatmo.net', 'monitoreverywhere.com',  'netpie.io',  'inatronic.com',    'fitdigits.com', 'riversongapp.net', 'orbitbhyve.com',  'utc.com', 'videoexpertsgroup.com', 'cloudlinks.cn', 'sleepace.com', 'veepai.com',  'vicohome.io', 'mygeostar.com', 'netatmo.com'  }

# def isIotRelatedSubdomain(subDomain):
#     subdomainSplitted = subDomain.split(".")
#     for domain in iotRelated:
#         iotDomainSplitted = domain.split(".")
#         if len(subdomainSplitted) < len(iotDomainSplitted):
#             continue
            
#         matched = True
#         for i in range(0, len(iotDomainSplitted)):
#             if iotDomainSplitted[len(iotDomainSplitted) - i -1] != subdomainSplitted[len(subdomainSplitted) -i -1]:
#                 matched = False
#                 break
            
#         if matched:
#             return True
            
        
#     return False

def getClassification(subDomain):
    if subDomain.endswith("."):
        return subDomain
    for key,item in exodusCategories.items():
        toReturn = key
        if key == 'otherExodus' or key == 'Advertisement':
            toReturn = "Advertisement and Trackers"
        if key == "Crash reporting":
            toReturn = 'Crash Reporting'
            
        subdomainSplitted = subDomain.split(".")
        for entry in item:
            entrySplitted = entry.split(".")
            if len(subdomainSplitted) >= len(entrySplitted):
                matched = True
                for i in range(0, len(entrySplitted)):
                    if entrySplitted[len(entrySplitted) - i - 1] != subdomainSplitted[len(subdomainSplitted) -i -1]:
                        matched = False
                        break
                if matched:
                    return toReturn
            
            
    if isCdnCategoryNew(subDomain):
        return "Content Distribution Networks"
    elif isAdCategoryNew(subDomain):
        return "Advertisement and Trackers"
    elif isSocialNetworkCategoryNew(subDomain):
        return "Social Networks"
    # elif isIotRelatedSubdomain(subDomain): # todo check
    #     return "IoT Related"
    
    return subDomain

dynamicSubDomains = []
iotscopeSubDomains = []

with open("domains_manual.json", "r") as dynamic:
    dynamicSubDomains = json.load(dynamic) 

with open("endpoints_iotscope_removed.json", "r") as iotscope:
    iotscopeSubDomains = json.load(iotscope) 

allSubDomains = set(dynamicSubDomains).union(set(iotscopeSubDomains))
#allSubDomains = set(iotscopeSubDomains)

classifiedMap = {}
for d in allSubDomains:
    classifiedMap[d] = getClassification(d)

numbers = {}

print(len(classifiedMap))

numbers['Others'] = []

for k,v in classifiedMap.items():
    if k == v:
        numbers['Others'].append(v)
    else:
        if v in numbers:
            numbers[v].append(k)
        else:
            numbers[v] = [k]

for k,v in numbers.items():
    print(k, str(len(v)))


json.dump(numbers, open('categories_union_new.json', 'w'))

#print(classifiedMap)    

'''
categoryId = {}
idCategory = {}
current = 4
for k,v in classifiedMap.items():
    if "." not in v and v not in categoryId:
        categoryId[v] =  current
        idCategory[current] = v
        current = current + 1

source = []
target = []
values = []
labels = []

valueDict = {}
        

for d in allSubDomains:
    targetId = 0
    if "." in classifiedMap[d]:
        targetId = 3
    else:
        targetId = categoryId[classifiedMap[d]]
        
        
    
    if d in dynamicSubDomains and d in iotscopeSubDomains:
        #source.append(1)
        #target.append(targetId)
        #values.append(1)
        key = f"1-{targetId}"
        valueDict[key] = valueDict.get(key, 0) + 1
    if d in dynamicSubDomains:
        key = f"0-{targetId}"
        valueDict[key] = valueDict.get(key, 0) + 1
        #source.append(0)
        #target.append(targetId)
        #values.append(1)
    elif d in iotscopeSubDomains:
        key = f"2-{targetId}"
        valueDict[key] = valueDict.get(key, 0) + 1
        #source.append(2)
        #target.append(targetId)
        #values.append(1)
        
for k,v in valueDict.items():
    sourceValue = k.split('-')[0]
    targetValue = k.split('-')[1]
    source.append(sourceValue)
    target.append(targetValue)
    values.append(valueDict[k])



labels.append("Dynamic Domains")
labels.append("Dynamic and Static Domains")
labels.append("Static Domains")
labels.append("Other")

for l in range(4,current):
    labels.append(idCategory[l])



link = dict(source = source, target = target, value = values)
node = dict(label = labels)
data = go.Sankey(link = link, node=node)
# plot
fig = go.Figure(data)
fig.show()
'''
