from ipwhois.utils import get_countries
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError

import logging
import pycountry
from .domainUtil import getIp


def mapToAlpha2CountryName(country):
    logging.debug('get alpha3 name of {}'.format(country))
    counryAlpha3 = None
    try:
        counryAlpha3 = pycountry.countries.get(alpha_2=country)
    except LookupError as e:
        logging.error('aplha name lookup failed for country: {} with error {}'.format(country, e))
        return "LookUPError"
    if counryAlpha3 == None:
        return country
    
    logging.debug("alpha3 is {} of {}".format(counryAlpha3.alpha_3, country))
    return counryAlpha3.alpha_3



def getCountry(ip):
    """
    docstring
    """
    obj = None
    logging.debug("looking for country of {}".format(ip))
    try:
        obj = IPWhois(ip)
    except IPDefinedError as e:
        logging.error('IP whois failed for ip: {} '.format(ip))
        return 'IP whois failed'
    
    if obj == None:
        logging.debug('obj is None')
        return 'IP whois none'
    # False for not including raw output into result
    res = obj.lookup_whois(False)

    countryCode = res['asn_country_code']
    if countryCode != None:
        country = mapToAlpha2CountryName(countryCode)
        if country != None and len(country) == 3:
            logging.debug("ip {} is from {}".format(ip, country))
            return country


    nets = res['nets']
    if nets == None:
        logging.debug('net is none')
        return "Nets None"

    alternativeResult = "Not Found"
    
    for net in nets:
        if net==None:
            logging.debug('first element of nets is None')
            return "No elem"

        if net['country'] == 'EU':
            alternativeResult = "EU"
        country = mapToAlpha2CountryName(net['country'])
        if country != None and len(country) == 3:
            logging.debug("ip {} is from {}".format(ip, country))
            return country
    
    return alternativeResult

    



def getCountries(domains):
    print(domains)
    statistic = {}
    for d in domains.keys():
        if d.startswith('.'):
            d = d[1:len(d)]
        ip = getIp(d)
        if ip == None:
            print(d)
            continue
        country = getCountry(ip)
        if country in statistic:
            statistic[country] = statistic[country] + domains[d]
        else:
            statistic[country] = domains[d]
    return statistic
