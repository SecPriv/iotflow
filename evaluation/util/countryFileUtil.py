import os
from .domainUtil import getIp
import pytricia
import pandas

result = pytricia.PyTricia(128) #{}

def loadIPs(path=""):
    for f in os.listdir(path):
        if f.endswith('cidr') or f.endswith('ipv6'):
            with open(path + f, "r") as openFile:
                name = os.path.basename(openFile.name).replace(".cidr", "").replace(".ipv6", "")
                #currentAddresses  = result.get(name, [])
                for line in openFile:
                    if line.startswith("#") or len(line.strip()) < 2:
                        continue

                    result.insert(line.strip(), name)
                    #result[ipaddress.ip_network(line.strip(), False)] = name
                    #currentAddresses.append(line.strip())

                #result[name] = currentAddresses
    return result



def findIP(ip):
    if result == {}:
        loadIPs()

    #for ipKey in result.keys():
    return result.get(ip)





def getCountries(domains):
    statistic = {}
    for d in domains.keys():
        if d.startswith('.'):
            d = d[1:len(d)]
        ip = getIp(d)
        if ip == None:
            print(f"could not find ip {d}")
            continue
        country = findIP(ip)
        if country in statistic:
            statistic[country] = statistic[country] + domains[d]
        else:
            statistic[country] = domains[d]
    return statistic



def getCountryFromIP(ip):

    if ip == None:
        print(f"could not find ip {d}")
        return None
    country = findIP(ip)
    return country

def getRows(data):
    countryName = []
    occurences = []
    for k in data.keys():
        countryName.append(k)
        occurences.append(data[k])

    return countryName, occurences


def createDataFrameFromStat(countryStat):
    names, occ = getRows(countryStat)
    stats = {'Countries': names, 'count': occ}
    return pandas.DataFrame.from_dict(stats)


