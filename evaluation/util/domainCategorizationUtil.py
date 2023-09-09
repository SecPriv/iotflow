import tldextract
import logging
from .domainUtil import getDomainOrIP
import re

def getCategoryMap(path):
    result = {}
    with open(path, "r") as f:
        for line in f:
            line = line.replace('\n', '')
            domain = ''
            commment = ''
            if line.startswith('#') or len(line) == 0:
                continue
            if ';' in line:
                splittedLine = line.split(';')
                domain = splittedLine[0]
                commment = splittedLine[1]
            elif ',' in line:
                splittedLine = line.split(',')
                domain = splittedLine[0]
                commment = splittedLine[1]
            else:
                domain = line
                commment = ''

            if domain.endswith('.'):
                domain = domain + "*"
            result[domain] = commment

    return result


advertisementMap = getCategoryMap('util/domainLists/3p_adtrackers.txt')
cdnMap = getCategoryMap('util/domainLists/3p_cdn.txt')
lumenMap = getCategoryMap('util/domainLists/3p_lumen.txt')
socialMap = getCategoryMap('util/domainLists/3p_social.txt')




def matchSubDomain(subdomain, categoryMap):
    if "amazonaws" in subdomain:
        print(subdomain)
    logging.debug("matching {}".format(subdomain))
    splittedDomain = subdomain.split('.')
    for entry in categoryMap.keys():
        logging.debug("Entry from the current category is {}".format(entry))
        splittedEntry = entry.split('.')
        if len(splittedEntry) > len(splittedDomain):
            continue

        matched = True
        for i in range(0, len(splittedEntry)):
            if "*" in splittedEntry[len(splittedEntry)-1-i]:
                starEntry = splittedEntry[len(splittedEntry)-1-i].split('*')
                if len(starEntry) == 0:
                    continue
                elif len(starEntry) == 1 and splittedEntry[len(splittedEntry)-1-i].startswith("*"):
                    if not splittedDomain[len(splittedDomain)-1-i].endswith(starEntry[0]):
                        matched = False
                        break
                elif len(starEntry) == 1:
                    if not splittedDomain[len(splittedDomain)-1-i].startswith(starEntry[0]):
                        matched = False
                        break
                elif len(starEntry) == 2:
                    if not splittedDomain[len(splittedDomain)-1-i].startswith(starEntry[0]) or not splittedDomain[len(splittedDomain)-1-i].endswith(starEntry[1]):
                        matched = False
                        break
                else:
                    logging.error("{} contains more than one wildcard".format(splittedEntry[len(splittedEntry)-1-i]))
            elif splittedEntry[len(splittedEntry)-1-i] != splittedDomain[len(splittedDomain)-1-i]:
                matched = False
                break
        if matched:
            print(subdomain + " matched")
            logging.debug("subdomain {} matched with {}".format(subdomain, entry))
            return True, categoryMap[entry]


    return False, ''



def matchSubDomainNew(subdomain, categoryMap):
    logging.debug("matching {}".format(subdomain))
    splittedDomain = subdomain.split('.')
    for entry in categoryMap.keys():
        logging.debug("Entry from the current category is {}".format(entry))
        splittedEntry = entry.split('.')
        matched = True
        if (len(splittedEntry) > 1 or len(splittedEntry) ==1) and len(splittedEntry)<=len(splittedDomain): # entry has subdomain and subdomain precise enough or entry has just domain
            for i in range(0, len(splittedEntry)):
                if "*" in splittedEntry[len(splittedEntry) - i -1]:
                    currentRegex = splittedEntry[len(splittedEntry) - i -1].replace("*", ".*")
                    if re.search(currentRegex, splittedDomain[len(splittedDomain) - i -1]) == None:
                        matched = False
                        break

                elif splittedEntry[len(splittedEntry) - i -1] != splittedDomain[len(splittedDomain) - i -1]:
                    matched = False
                    break
        else:
            # subdomain not precise enough for entry
            matched = False


        if matched:
            print(subdomain + " matched")
            logging.debug("subdomain {} matched with {}".format(subdomain, entry))
            return True, categoryMap[entry]

    return False, ''

def getCategoriesForApp(appDomainData):
    result = {}
    for subdomain in appDomainData.keys():
        ad,commentAd = matchSubDomain(subdomain,advertisementMap )
        cdn,commentCdn = matchSubDomain(subdomain,cdnMap )
        lumen,commentLumen = matchSubDomain(subdomain,lumenMap )
        social,commentSocial = matchSubDomain(subdomain, socialMap)

        if ad:
            result['Advertisement and Trackers'] = result.get('Advertisement and Trackers', 0) + 1
        elif cdn:
            result['Content Distribution Networks'] = result.get('Content Distribution Networks', 0) + 1
        elif lumen:
            result['Advertisement and Trackers'] = result.get('Advertisement and Trackers', 0) + 1
        elif social:
            result['Social Networks'] = result.get('Social Networks', 0) + 1
        else:
            result[getDomainOrIP(subdomain)] = result.get(getDomainOrIP(subdomain), 0) +1
            #result['noCategory'] = result.get('noCategory', 0) + 1
    return result

def isAdCategory(subdomain):
    ad,commentAd = matchSubDomain(subdomain,advertisementMap)
    lumen,commentLumen = matchSubDomain(subdomain,lumenMap)

    if ad or lumen:
        return True

    return False


def isCdnCategory(subdomain):
    cdn,commentCdn = matchSubDomain(subdomain,cdnMap )
    if cdn:
        return True

    return False

def isSocialNetworkCategory(subdomain):
    social,commentSocial = matchSubDomain(subdomain, socialMap)
    if social:
        return True

    return False



def isAdCategoryNew(subdomain):
    ad,commentAd = matchSubDomainNew(subdomain,advertisementMap)
    lumen,commentLumen = matchSubDomainNew(subdomain,lumenMap)

    if ad or lumen:
        return True

    return False


def isCdnCategoryNew(subdomain):
    cdn,commentCdn = matchSubDomainNew(subdomain,cdnMap )
    if cdn:
        return True

    return False

def isSocialNetworkCategoryNew(subdomain):
    social,commentSocial = matchSubDomainNew(subdomain, socialMap)
    if social:
        return True

    return False
