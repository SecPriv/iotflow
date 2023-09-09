import re
from typing import Set
from urlextract import URLExtract

extractor = URLExtract()


def can_be_valid(ip_string: str) -> bool:
    ip_string = ip_string.strip()
    splitted_ip = ip_string.split(".")
    if len(splitted_ip) != 4:
        return False

    for item in splitted_ip:
        if int(item) < 0 or int(item) > 255:
            return False

    return True


def get_urlextract_results(value_scope_string: str):
    return extractor.find_urls(value_scope_string)


def parse_ip_or_domain(value_scope_string: str):
    result: Set[str] = set()
    ip_extract = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', value_scope_string)
    if len(ip_extract) > 0:
        for c in ip_extract:
            if can_be_valid(c):
                result.add(c)

    for ip in result:
        value_scope_string = value_scope_string.replace(ip, "")

    result.update(get_urlextract_results(value_scope_string))
    return result


def parse_all(value_scope_results) -> Set[str]:
    result: Set[str] = set()
    for vs in value_scope_results:
        result.update(parse_ip_or_domain(vs))

    return result
