import json, tldextract

MANUAL_CATEGORIES = json.load(open('categories_manual_new.json', 'r'))
IOTFLOW_CATEGORIES = json.load(open('categories_iotflow_new.json', 'r'))

IOTFLOW_NUMBER_DOMAINS = 0
IOTFLOW_NUMBER_TLD = 0


def get_top_level_domains(e_list):

    tl_domains = set()

    for e in e_list:
        tldextract_res = tldextract.extract(e)
        # print(e)
        # print(tldextract_res)

        if tldextract_res.suffix != '':
            tl_domain = tldextract_res.domain + '.' + tldextract_res.suffix
        else:
            tl_domain = tldextract_res.domain
        tl_domains.add(tl_domain)

    return tl_domains

def check_intersection(v_list, m_list):
    intersect = []
    for tl in v_list:
        if tl in m_list:
            intersect.append(tl)

    return intersect

INTERSECTION = {}

def union(A, B):
    for a in A:
        B.add(a)
    return len(B)

IOTFLOW_TLD_CAEGORIES = {}
MANUAL_TLD_CATEGORIES = {}

for cat, domains in MANUAL_CATEGORIES.items():
    tl_manual = get_top_level_domains(MANUAL_CATEGORIES[cat])
    MANUAL_TLD_CATEGORIES[cat] = list(tl_manual)

    tl_iotflow = get_top_level_domains(IOTFLOW_CATEGORIES[cat])
    IOTFLOW_TLD_CAEGORIES[cat] = list(tl_iotflow)

    #IOTFLOW_NUMBER_DOMAINS += len(MANUAL_CATEGORIES[cat])

    intersect = check_intersection(tl_iotflow, tl_manual)

    print("Total IoTFlow TLDs in ", cat, ":", len(tl_iotflow))
    print("Total Manual TLDs in ", cat, ":", len(tl_manual))

    print("Union of TLDs for ", cat, union(tl_iotflow, tl_manual))

    IOTFLOW_NUMBER_TLD += len(tl_manual)

    INTERSECTION[cat] = intersect

    print("Intersecting values for", cat + ':', len(intersect), '(', len(intersect)/union(tl_iotflow, tl_manual)*100, '%)')

#print(IOTFLOW_NUMBER_DOMAINS)
#print(IOTFLOW_NUMBER_TLD)

#json.dump(INTERSECTION, open('tld_intersection.json', 'w'))
json.dump(IOTFLOW_TLD_CAEGORIES, open('tld_iotflow_new.json', 'w'))
json.dump(MANUAL_TLD_CATEGORIES, open('tld_manual_new.json', 'w'))
