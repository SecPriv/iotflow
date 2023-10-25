
import re
import tldextract
import json
import socket
import logging

#|^(.*\.local.*)
localNetwork = re.compile("(192\.168\.\d\d?\d?\.\d\d?\d?)|(10\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)|(172\.1[6-9]\.\d\d?\d?\.\d\d?\d?)|(172\.2[0-9]\.\d\d?\d?\.\d\d?\d?)|(172\.3[0-1]\.\d\d?\d?\.\d\d?\d?)|(.*[^:]fromUI\.local[:\/ ])")
localIp = re.compile("(^127\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?.*)|(^(.*:?\/?\/?)::1.*)|(^0\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?.*)")
ip = re.compile("\d\d?\d?.\d\d?\d?\.\d\d?\d?\.\d\d?\d?")

def isLocal(d):
    if localNetwork.match(d) or localIp.match(d):
        return True

    return False



def getDomainOrIP(d):
    extractedSubdomain = tldextract.extract(d)
    if ip.match(extractedSubdomain.domain):
        return extractedSubdomain.domain
    return extractedSubdomain.domain + '.' + extractedSubdomain.suffix


def getIp(hostname):
    """
    docstring
    """
    logging.debug('search for ip of {}'.format(hostname))
    try:
        return socket.gethostbyname(hostname)
    except UnicodeError as e:
        logging.error('{} not found'.format(hostname))
        return None
    except socket.gaierror as e:
        logging.error('{} not found'.format(hostname))
        return None

def generateTotalCount(listApps, previousCounts):
    for app in listApps:

        for domain in app.keys():
            countedValue = previousCounts.get(domain, 0)

            countedValue = countedValue + app.get(domain)
            previousCounts[domain] = countedValue

    return previousCounts


def generateTotalCountMapping(listApps, previousCounts, mapping):
    for app in listApps:

        for domain in app.keys():
            #print(domain)
            try:
                countedValue = previousCounts.get(mapping[domain], 0)
                countedValue = countedValue + app.get(domain)
                previousCounts[mapping[domain]] = countedValue
            except KeyError as e:
                print(f"could not find {domain}")


    return previousCounts

def subListAppsToListApps(listApps):
    result = []
    for app in listApps:
        temp = set()
        for domain in app:
            splittedDomain = domain.split('.')
            temp.add(splittedDomain[len(splittedDomain)-2] + '.' + splittedDomain[len(splittedDomain)-1])
        result.append(temp)

    return result




def validateSubDomains(subdomains):
    result = {}
    notFound = []
    for sub in subdomains:
        extracted = tldextract.extract(sub)
        sub = extracted.subdomain +'.' + extracted.domain + '.'+ extracted.suffix
        if sub.startswith("."):
            sub = sub[1:len(sub)]

        if sub not in notFound and extracted.suffix != '' and getIp(sub) != None:
            result[sub] = 1
        else:
            notFound.append(sub)

    return result


def countAndValidateSubDomains(subdomains, countSubdomains):
    result = {}
    notFound = []
    ip = re.compile('\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?')
    for sub in subdomains:
        if ip.match(sub) == None:
            extracted = tldextract.extract(sub)
            domain = extracted.domain + '.'+ extracted.suffix
            if domain.startswith("."):
                domain = domain[1:len(domain)]
            if domain not in notFound and extracted.suffix != '' and getIp(domain) != None:
                if countSubdomains:
                    result[domain] = result.get(domain, 0) + 1
                else:
                    result[domain] = 1
            else:
                notFound.append(domain)
        else:
            if not localIp.match(sub) and not localNetwork.match(sub):
                result[sub] = result.get(sub, 0) + 1

    return result

def getSanitzedApps(appList, subdomainStat, countSubDomain):
    sanitizedAppList = []
    if subdomainStat:
        for app in appList:
            sanitizedAppList.append(validateSubDomains(app))
    else:
        for app in appList:
            sanitizedAppList.append(countAndValidateSubDomains(app, countSubDomain))
    return sanitizedAppList